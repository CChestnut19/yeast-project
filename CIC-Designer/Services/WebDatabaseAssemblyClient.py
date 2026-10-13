import os
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from dotenv import dotenv_values
from urllib3.util.retry import Retry


class AssemblyAPIError(RuntimeError):
    pass


class WebDatabaseAssemblyClient:
    def __init__(
        self,
        base_url,
        token,
        session=None,
        sleep=time.sleep,
        monotonic=time.monotonic,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = session or requests.Session()
        if session is None:
            retry = Retry(
                total=4,
                connect=4,
                read=4,
                status=4,
                backoff_factor=0.5,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset({'GET', 'POST'}),
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
        self._sleep = sleep
        self._monotonic = monotonic
        self._csrf_token = None

    @classmethod
    def from_env(
        cls,
        env_path=None,
        session_factory=requests.Session,
        sleep=time.sleep,
        monotonic=time.monotonic,
    ):
        path = (
            Path(env_path)
            if env_path
            else Path(__file__).resolve().parents[1] / ".env"
        )
        file_values = dotenv_values(path)
        values = {
            "BioApp_API_URL": os.getenv("BIOAPP_API_URL") or file_values.get("BIOAPP_API_URL") or file_values.get("WebDatabase_URL"),
            "token": os.getenv("BIOAPP_TOKEN") or file_values.get("BIOAPP_TOKEN"),
        }
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise AssemblyAPIError(
                "Missing required configuration: " + ", ".join(missing)
            )
        return cls(
            values["BioApp_API_URL"],
            values["token"],
            session_factory(),
            sleep,
            monotonic,
        )

    def _request(self, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        if self.token:
            headers["Token"] = self.token
        kwargs["headers"] = headers
        response = None
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            status = (
                f" HTTP {response.status_code}"
                if response is not None
                else ""
            )
            body = ''
            if response is not None:
                try:
                    body = (response.text or '')[:500]
                except Exception:
                    body = ''
            detail = f"; response={body}" if body else ''
            raise AssemblyAPIError(
                f"bio-app request failed:{status} {method} {url}; "
                f"cause={exc}{detail}"
            ) from exc

    @staticmethod
    def _json(response, context):
        try:
            data = response.json()
        except (TypeError, ValueError) as exc:
            raise AssemblyAPIError(
                f"{context} returned invalid JSON"
            ) from exc
        if not isinstance(data, dict):
            raise AssemblyAPIError(f"{context} returned invalid JSON")
        return data

    def login(self):
        if not self.token:
            raise AssemblyAPIError("bio-app Token is required")

    def get_part_id(self, name):
        response = self._request(
            "GET",
            f"{self.base_url}/WebDatabase/PartID",
            params={"name": name},
            timeout=30,
        )
        part_id = self._json(
            response, f"Part ID lookup for {name}"
        ).get("PartID")
        if part_id is None:
            raise AssemblyAPIError(f"Part ID lookup failed for {name}")
        return part_id

    def submit_assembly(self, payload, stage):
        body = {
            "name": payload.get("uuid"),
            "parts": payload.get("part", []),
            "backbones": payload.get("backbone", []),
            "plasmids": payload.get("plasmid", []),
            "scar": payload.get("scar", []),
            "level": 2 if stage == "Level2" else 3,
            "enzyme": payload.get("enzyme", "auto"),
        }
        response = self._request(
            "POST",
            f"{self.base_url}/assembly/run",
            json=body,
            timeout=30,
        )
        data = self._json(response, f"{stage} submission")
        if data.get("status") != 1:
            if data.get("status") in (2, 4):
                raise AssemblyAPIError(
                    "bio-app authentication failed: Token is missing, expired, or disabled"
                )
            raise AssemblyAPIError(
                data.get("msg") or f"{stage} submission was rejected by bio-app"
            )
        task_id = data.get("options", {}).get("taskId")
        if not task_id:
            raise AssemblyAPIError(
                f"{stage} submission returned no task_id"
            )
        return task_id

    def wait_for_task(self, task_id, stage, timeout=300, interval=1):
        start = self._monotonic()
        url = f"{self.base_url}/assembly/tasks/{task_id}"
        while self._monotonic() - start <= timeout:
            data = self._json(
                self._request("GET", url, timeout=30),
                f"{stage} task status",
            )
            task = data.get("options", {}).get("task", {})
            if task.get("status") == "completed":
                result = task.get("result")
                if not isinstance(result, dict):
                    raise AssemblyAPIError(
                        f"{stage} completed without a valid result"
                    )
                return result
            if task.get("status") == "failed":
                message = (
                    task.get("errorMsg")
                    or "unknown error"
                )
                raise AssemblyAPIError(f"{stage} failed: {message}")
            self._sleep(interval)
        raise AssemblyAPIError(f"{stage} task timed out")

    def download_result(self, download_url, destination):
        target = Path(destination)
        partial = Path(f"{target}.part")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = self._request(
                "GET",
                urljoin(f"{self.base_url}/", download_url),
                stream=True,
                timeout=60,
            )
            with partial.open("wb") as output:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        output.write(chunk)
            if not partial.exists() or partial.stat().st_size == 0:
                raise AssemblyAPIError(
                    "Assembly result download returned an empty file"
                )
            os.replace(partial, target)
            return str(target)
        except Exception:
            if partial.exists():
                partial.unlink()
            raise
