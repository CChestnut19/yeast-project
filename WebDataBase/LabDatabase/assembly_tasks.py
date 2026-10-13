"""Durable state and scoped idempotency for assembly submissions."""
import uuid
from django.db import IntegrityError, OperationalError, close_old_connections, connections, transaction
from .feature_records import digest


MYSQL_CONNECTION_LOST_CODES = {2006, 2013}


def _is_mysql_connection_lost(exc):
    return bool(exc.args) and exc.args[0] in MYSQL_CONNECTION_LOST_CODES


def _update_once(task_id, state):
    from WebDatabase.models import AssemblyTask
    with transaction.atomic():
        task = AssemblyTask.objects.select_for_update().filter(pk=task_id).first()
        if not task:
            return
        task.state = dict(task.state, **state, task_id=task_id, execution_mode=task.execution_mode)
        task.save(update_fields=['state', 'updated_at'])


def register(request, target, mode, request_id=None):
    from WebDatabase.models import AssemblyTask
    info = request.session.get('info') or {}
    owner = str(info.get('uid') or info.get('id') or request.user.pk or '')
    key = digest([owner, target, mode, str(request_id)]) if request_id else None
    try:
        with transaction.atomic():
            task = AssemblyTask.objects.create(id=str(uuid.uuid4()), request_key=key,
                owner_id=owner, target=target, execution_mode=mode,
                state={'status': 'processing', 'phase': 'queued', 'progress': 0})
        return task, True
    except IntegrityError:
        if key is None:
            raise
        return AssemblyTask.objects.get(request_key=key), False


def update(task_id, **state):
    close_old_connections()
    try:
        _update_once(task_id, state)
    except OperationalError as exc:
        if not _is_mysql_connection_lost(exc):
            raise
        # Thread-pool workers can retain a connection longer than MySQL's
        # wait_timeout. Discard it and retry this idempotent state update once.
        connections['default'].close()
        _update_once(task_id, dict(state, retry_performed=True))


def sync_cache(task_id, cache_obj):
    if cache_obj:
        update(task_id, status=cache_obj.getStatus(), progress=cache_obj.getProgress(),
               message=cache_obj.getMessage() or '', result=cache_obj.getResult(),
               success=cache_obj.getStatus() == 'completed')
