"""Filesystem-backed upload task storage for fitting requests."""

import json
import os
import shutil
import time
import uuid
from pathlib import Path


METADATA_FILE = "metadata.json"


def _task_ttl_seconds():
    return max(60, int(os.getenv("UPLOAD_TASK_TTL_SECONDS", "86400")))


def _task_directory(upload_root, upload_id):
    try:
        normalized_id = str(uuid.UUID(str(upload_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Invalid upload_id") from exc
    return Path(upload_root).resolve() / normalized_id


def cleanup_expired_tasks(upload_root):
    root = Path(upload_root).resolve()
    if not root.exists():
        return
    expires_before = time.time() - _task_ttl_seconds()
    for directory in root.iterdir():
        metadata_path = directory / METADATA_FILE
        if not directory.is_dir() or not metadata_path.is_file():
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            created_at = float(metadata["created_at"])
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            continue
        if created_at < expires_before:
            shutil.rmtree(directory, ignore_errors=True)


def create_upload_task(upload_root, uploaded_files):
    root = Path(upload_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    cleanup_expired_tasks(root)

    upload_id = str(uuid.uuid4())
    task_directory = root / upload_id
    task_directory.mkdir()
    saved_files = []
    try:
        for uploaded_file, safe_name in uploaded_files:
            candidate = safe_name
            stem = Path(safe_name).stem
            suffix = Path(safe_name).suffix
            counter = 2
            while (task_directory / candidate).exists():
                candidate = f"{stem}-{counter}{suffix}"
                counter += 1
            uploaded_file.save(task_directory / candidate)
            saved_files.append(candidate)

        metadata = {
            "upload_id": upload_id,
            "created_at": time.time(),
            "files": saved_files,
        }
        (task_directory / METADATA_FILE).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return metadata
    except Exception:
        shutil.rmtree(task_directory, ignore_errors=True)
        raise


def get_upload_task_files(upload_root, upload_id):
    task_directory = _task_directory(upload_root, upload_id)
    metadata_path = task_directory / METADATA_FILE
    if not metadata_path.is_file():
        raise ValueError("Upload task was not found or has expired")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if float(metadata["created_at"]) < time.time() - _task_ttl_seconds():
        shutil.rmtree(task_directory, ignore_errors=True)
        raise ValueError("Upload task has expired")

    files = []
    for filename in metadata.get("files", []):
        file_path = (task_directory / filename).resolve()
        if file_path.parent != task_directory or not file_path.is_file():
            raise ValueError("Upload task metadata contains an invalid file")
        files.append(str(file_path))
    if not files:
        raise ValueError("Upload task contains no files")
    return files
