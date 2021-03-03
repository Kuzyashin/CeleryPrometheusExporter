from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4


class BaseEvent(BaseModel):
    hostname: str
    utcoffset: int
    pid: int
    clock: int
    timestamp: datetime
    local_received: datetime
    

class BaseUUIDEvent(BaseEvent):
    uuid: UUID4


class TaskSentEvent(BaseUUIDEvent):
    name: str
    args: str
    kwargs: str
    retries: int
    eta: Optional[datetime]
    expires: Optional[datetime]
    queue: str
    exchange: str
    routing_key: str
    root_id: UUID4
    parent_id: Optional[UUID4]


class TaskReceivedEvent(BaseUUIDEvent):
    name: str
    args: str
    kwargs: str
    retries: int
    eta: Optional[datetime]
    expires: Optional[datetime]
    root_id: UUID4
    parent_id: Optional[UUID4]


class TaskStartedEvent(BaseUUIDEvent):
    ...


class TaskSucceededEvent(BaseUUIDEvent):
    result: Optional[str]
    runtime: float


class TaskFailedEvent(BaseUUIDEvent):
    exception: str
    traceback: str


class TaskRejectedEvent(BaseUUIDEvent):
    requeued: bool
    

class TaskRevokedEvent(BaseUUIDEvent):
    terminated: bool
    signum: int
    expired: bool
    

class TaskRetriedEvent(BaseUUIDEvent):
    exception: str
    traceback: str
    expired: bool


class WorkerEvent(BaseEvent):
    freq: int
    sw_ident: Optional[str]
    sw_ver: Optional[str]
    sw_sys: Optional[str]
    active: Optional[int]
    processed: Optional[int]
    loadavg: Optional[List[float]]


