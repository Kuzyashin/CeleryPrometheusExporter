from prometheus_client import Counter, Gauge, Histogram
from prometheus_client.registry import CollectorRegistry

registry = CollectorRegistry(auto_describe=True)

celery_tasks_status = Counter(
    name='celery_tasks_status', documentation='Tasks statuses',
    registry=registry, labelnames=('name', 'hostname', 'state',)
)
celery_tasks_sent = Counter(
    name='celery_tasks_sent', documentation='Tasks sent to workers',
    registry=registry, labelnames=('name', 'hostname',)
)
celery_tasks_received = Counter(
    name='celery_tasks_received', documentation='Tasks received by workers',
    registry=registry, labelnames=('name', 'hostname')
)
celery_tasks_started = Counter(
    name='celery_tasks_started', documentation='Tasks started by workers',
    registry=registry, labelnames=('name', 'hostname',)
)
celery_tasks_succeeded = Counter(
    name='celery_tasks_succeeded', documentation='Tasks completed by workers',
    registry=registry, labelnames=('name', 'hostname',)
)
celery_tasks_failed = Counter(
    name='celery_tasks_failed', documentation='Tasks failed by workers',
    registry=registry, labelnames=('name', 'hostname', 'exectype',)
)
celery_tasks_rejected = Counter(
    name='celery_tasks_rejected', documentation='Tasks rejected by workers',
    registry=registry, labelnames=('name', 'hostname',)
)
celery_tasks_revoked = Counter(
    name='celery_tasks_revoked', documentation='Tasks sent to workers',
    registry=registry, labelnames=('name', 'hostname',)
)
celery_tasks_retried = Counter(
    name='celery_tasks_retried', documentation='Tasks retried by workers',
    registry=registry, labelnames=('name', 'hostname', 'exectype',)
)
celery_tasks_processed_time = Histogram(
    name='celery_tasks_execution_time', documentation='Task execution time',
    registry=registry, labelnames=('name', 'hostname', 'state'),
    buckets=[0.5, 2, 5, 10, 20, 30, 60, 120]
)
celery_tasks_active = Gauge(
    name='celery_tasks_active', documentation='Count of active tasks',
    registry=registry, labelnames=('name', 'hostname'),
)
celery_workers_active = Gauge(
    name='celery_workers_active', documentation='Count of active workers',
    registry=registry,
)
celery_workers_up = Gauge(
    name='celery_workers_up', documentation='Worker up info',
    registry=registry, labelnames=('hostname',)
)
celery_workers_load = Gauge(
    name='celery_workers_load', documentation='Worker load info',
    registry=registry, labelnames=('hostname', 'load_type',)
)
