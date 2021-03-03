import time

from celery import Celery
from celery.events.state import Task, State, Worker
from prometheus_client import start_http_server

from events import TaskSentEvent, TaskReceivedEvent, TaskStartedEvent, TaskSucceededEvent, TaskFailedEvent, \
    TaskRejectedEvent, TaskRevokedEvent, TaskRetriedEvent, WorkerEvent
from prometheus import celery_tasks_sent, celery_tasks_failed, celery_tasks_retried, celery_tasks_revoked, \
    celery_tasks_received, celery_tasks_rejected, \
    celery_tasks_succeeded, celery_tasks_started, registry, celery_tasks_processed_time, celery_tasks_active, \
    celery_workers_active, celery_workers_up, \
    celery_workers_load, celery_tasks_status


class Monitor(object):
    
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app
        self.state: State = celery_app.events.State()
        self.wait_for_app()
        self.set_active_celery_tasks_count()
        self.set_active_workers_count()
    
    def wait_for_app(self):
        inspector = self.celery_app.control.inspect()
        while not inspector.active():
            time.sleep(10)
    
    def set_active_celery_tasks_count(self):
        inspector = self.celery_app.control.inspect()
        active = inspector.active()
        for tasks in active.values():
            for task in tasks:
                celery_tasks_active.labels(task['name'], task['hostname']).inc()
    
    def set_active_workers_count(self):
        inspector = self.celery_app.control.inspect()
        registered = inspector.registered()
        workers_count = len(registered)
        celery_workers_active.set(workers_count)
        for worker in registered:
            celery_workers_up.labels(worker).set(1)
    
    def task_sent(self, event: dict):
        self.state.event(event)
        event = TaskSentEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_sent.labels(task.name, event.hostname).inc()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_received(self, event: dict):
        self.state.event(event)
        event = TaskReceivedEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_received.labels(task.name, event.hostname).inc()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_started(self, event: dict):
        self.state.event(event)
        event = TaskStartedEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_started.labels(task.name, event.hostname).inc()
        celery_tasks_active.labels(task.name, event.hostname).inc()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_succeeded(self, event: dict):
        self.state.event(event)
        event = TaskSucceededEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_succeeded.labels(task.name, event.hostname).inc()
        celery_tasks_processed_time.labels(task.name, event.hostname, task.state).observe(task.runtime)
        celery_tasks_active.labels(task.name, event.hostname).dec()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_failed(self, event: dict):
        self.state.event(event)
        event = TaskFailedEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_failed.labels(task.name, event.hostname, event.exception).inc()
        celery_tasks_active.labels(task.name, event.hostname).dec()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_rejected(self, event: dict):
        self.state.event(event)
        event = TaskRejectedEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_rejected.labels(task.name, event.hostname).inc()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_revoked(self, event: dict):
        self.state.event(event)
        event = TaskRevokedEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_revoked.labels(task.name, event.hostname).inc()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def task_retried(self, event: dict):
        self.state.event(event)
        event = TaskRetriedEvent.parse_obj(event)
        task: Task = self.state.tasks.get(str(event.uuid))
        celery_tasks_retried.labels(task.name, event.hostname, event.exception).inc()
        celery_tasks_status.labels(task.name, event.hostname, task.state).inc()
    
    def worker_online(self, event: dict):
        self.state.event(event)
        event = WorkerEvent.parse_obj(event)
        worker: Worker = self.state.workers.get(event.hostname)
        celery_workers_active.inc()
        celery_workers_up.labels(event.hostname).set(1)
    
    def worker_offline(self, event: dict):
        self.state.event(event)
        event = WorkerEvent.parse_obj(event)
        worker: Worker = self.state.workers.get(event.hostname)
        celery_workers_active.dec()
        celery_workers_up.labels(event.hostname).set(0)
    
    def worker_heartbeat(self, event: dict):
        self.state.event(event)
        event = WorkerEvent.parse_obj(event)
        worker: Worker = self.state.workers.get(event.hostname)
        celery_workers_up.labels(event.hostname).set(1)
        if event.loadavg:
            celery_workers_load.labels(event.hostname, 'short').set(event.loadavg[0])
            celery_workers_load.labels(event.hostname, 'medium').set(event.loadavg[1])
            celery_workers_load.labels(event.hostname, 'long').set(event.loadavg[2])
    
    def run(self):
        with self.celery_app.connection() as connection:
            recv = app.events.Receiver(connection, handlers={
                '*': self.state.event,
                'task-sent': self.task_sent,
                'task-received': self.task_received,
                'task-started': self.task_started,
                'task-succeeded': self.task_succeeded,
                'task-failed': self.task_failed,
                'task-rejected': self.task_rejected,
                'task-revoked': self.task_revoked,
                'task-retried': self.task_retried,
                'worker-heartbeat': self.worker_heartbeat,
                'worker-online': self.worker_online,
                'worker-offline': self.worker_offline
            })
            recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == '__main__':
    import os
    
    BROKER_USERNAME = os.environ.get('BROKER_USERNAME', 'django')
    BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', 'django')
    BROKER_HOST = os.environ.get('BROKER_HOST', 'localhost')
    BROKER_PORT = os.environ.get('BROKER_PORT', '2233')
    
    app = Celery(broker=f'amqp://{BROKER_USERNAME}:{BROKER_PASSWORD}@{BROKER_HOST}:{BROKER_PORT}//')
    monitor = Monitor(app)
    start_http_server(port=8100, registry=registry)
    
    monitor.run()
