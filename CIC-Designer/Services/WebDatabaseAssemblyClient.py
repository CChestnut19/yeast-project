"""Session-based client for the Django WebDatabase assembly endpoints."""
import os
import time
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit

import requests
from requests.adapters import HTTPAdapter
from dotenv import dotenv_values
from urllib3.util.retry import Retry


class AssemblyAPIError(RuntimeError):
    pass


class WebDatabaseAssemblyClient:
    def __init__(self, base_url, session=None, *, username=None, password=None,
                 sleep=time.sleep, monotonic=time.monotonic):
        self.base_url = base_url.rstrip('/')
        if self.base_url.lower().endswith('/webdatabase'):
            self.base_url = self.base_url[:-len('/WebDatabase')]
        self.username = username
        self.password = password
        self.session = session if session is not None else requests.Session()
        # Submission is not idempotent: never automatically retry a POST.
        adapter = HTTPAdapter(max_retries=Retry(
            total=4, connect=0, read=4, status=4, backoff_factor=.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({'GET'})))
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self._sleep = sleep
        self._monotonic = monotonic

    @classmethod
    def from_env(cls, env_path=None, session_factory=requests.Session,
                 sleep=time.sleep, monotonic=time.monotonic, base_url=None):
        path = Path(env_path) if env_path else Path(__file__).resolve().parents[1] / '.env'
        values = dotenv_values(path)
        def setting(*names):
            return next((os.getenv(name) or values.get(name) for name in names
                         if os.getenv(name) or values.get(name)), None)
        base_url = base_url or setting('WebDatabase_URL', 'BIOAPP_API_URL')
        if not base_url:
            raise AssemblyAPIError('Missing WebDatabase_URL configuration')
        return cls(base_url, session_factory(),
                   # Windows USERNAME is case-insensitive; prefer the local login value.
                   username=(setting('WEBDATABASE_USERNAME') or values.get('username')
                             or os.getenv('username')),
                   password=(setting('WEBDATABASE_PASSWORD') or values.get('password')
                             or os.getenv('password')),
                   sleep=sleep, monotonic=monotonic)

    def _request(self, method, url, **kwargs):
        headers = dict(kwargs.pop('headers', {}) or {})
        if method.upper() not in {'GET', 'HEAD', 'OPTIONS'}:
            csrf = self.session.cookies.get('csrftoken')
            if not csrf:
                raise AssemblyAPIError('WebDatabase CSRF cookie is missing; log in first')
            headers['X-CSRFToken'] = csrf
            headers['Referer'] = f'{self.base_url}/WebDatabase/login'
        kwargs['headers'] = headers
        kwargs.setdefault('allow_redirects', False)
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            raise AssemblyAPIError(
                f'WebDatabase {method} request failed' +
                (f' (HTTP {status})' if status is not None else '')
            ) from exc

    @staticmethod
    def _json(response, context):
        if 300 <= response.status_code < 400:
            raise AssemblyAPIError(f'{context} redirected; check WebDatabase login')
        try:
            data = response.json()
        except (TypeError, ValueError) as exc:
            raise AssemblyAPIError(f'{context} returned invalid JSON') from exc
        if not isinstance(data, dict):
            raise AssemblyAPIError(f'{context} returned invalid JSON')
        return data

    def login(self):
        login_url = f'{self.base_url}/WebDatabase/login'
        response = self._request('GET', login_url, timeout=30)
        expected = urlsplit(f'{self.base_url}/LabDatabase/index')
        def logged_in(reply):
            destination = urlsplit(urljoin(login_url, reply.headers.get('Location', '')))
            return (reply.status_code in (302, 303) and
                    (destination.scheme, destination.netloc, destination.path) ==
                    (expected.scheme, expected.netloc, expected.path) and
                    bool(self.session.cookies.get('sessionid')))
        if logged_in(response):
            return
        if not self.username or not self.password:
            raise AssemblyAPIError(
                'Assembly requires WebDatabase username/password in CIC-Designer/.env')
        response = self._request('POST', login_url, timeout=30,
                                 data={'username': self.username, 'password': self.password})
        if not logged_in(response):
            raise AssemblyAPIError('WebDatabase login failed; check username/password')

    def get_part_id(self, name):
        response = self._request('GET', f'{self.base_url}/WebDatabase/PartID',
                                 params={'name': name}, timeout=30)
        part_id = self._json(response, 'Part ID lookup').get('PartID')
        if part_id is None:
            raise AssemblyAPIError(f'Part ID lookup failed for {name}')
        return part_id

    def get_plasmid_name(self, plasmid_id):
        response = self._request('GET', f'{self.base_url}/WebDatabase/PlasmidNameByID',
                                 params={'ID': plasmid_id}, timeout=30)
        name = self._json(response, 'Plasmid name lookup').get('PlasmidName')
        if not isinstance(name, str) or not name:
            raise AssemblyAPIError('Assembly result plasmid name was not found')
        return name

    def submit_assembly(self, payload, stage):
        body = {'uuid': payload['uuid'], 'part': payload.get('part', []),
                'backbone': payload.get('backbone', []),
                'plasmid': payload.get('plasmid', []), 'scar': payload.get('scar', [])}
        response = self._request('POST', f'{self.base_url}/LabDatabase/AssemblyWithoutRepo',
                                 json=body, timeout=30)
        data = self._json(response, f'{stage} submission')
        task_id = data.get('task_id')
        if data.get('success') is False or data.get('status') == 'failed' or not task_id:
            raise AssemblyAPIError(data.get('message') or f'{stage} submission failed')
        return task_id

    def wait_for_task(self, task_id, stage, timeout=300, interval=1):
        start = self._monotonic()
        url = f'{self.base_url}/LabDatabase/task_status/{quote(str(task_id), safe="")}'
        while self._monotonic() - start <= timeout:
            data = self._json(self._request('GET', url, timeout=30), f'{stage} task status')
            if data.get('status') == 'failed' or data.get('success') is False:
                raise AssemblyAPIError(data.get('error') or data.get('message') or f'{stage} failed')
            if data.get('status') == 'completed':
                result = data.get('result')
                if not isinstance(result, dict) or result.get('success') is False:
                    raise AssemblyAPIError(f'{stage} completed without a valid result')
                return result
            self._sleep(interval)
        raise AssemblyAPIError(f'{stage} task timed out')

    def download_result(self, download_url, destination):
        url = urljoin(f'{self.base_url}/', download_url)
        base, target_url = urlsplit(self.base_url), urlsplit(url)
        if (target_url.scheme, target_url.netloc) != (base.scheme, base.netloc):
            raise AssemblyAPIError('Assembly download must use the WebDatabase host')
        target = Path(destination)
        partial = Path(f'{target}.part')
        target.parent.mkdir(parents=True, exist_ok=True)
        response = None
        try:
            response = self._request('GET', url, stream=True, timeout=60)
            content_type = response.headers.get('Content-Type', '').lower()
            if response.status_code != 200 or 'json' in content_type or 'html' in content_type:
                raise AssemblyAPIError('Assembly download did not return a file')
            with partial.open('wb') as output:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        output.write(chunk)
            if partial.stat().st_size == 0:
                raise AssemblyAPIError('Assembly download returned an empty file')
            os.replace(partial, target)
            return str(target)
        except Exception:
            if partial.exists():
                partial.unlink()
            raise
        finally:
            if response is not None:
                response.close()
