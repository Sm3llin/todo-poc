from dataclasses import dataclass
from typing import Optional

from events import Event


class TodoEvent:
    __topic__ = "todo-stuff"


@dataclass(frozen=True)
class TodoCreated(Event, TodoEvent):
    todo_id: int
    title: str
    description: str = ""


@dataclass(frozen=True)
class TodoModified(Event, TodoEvent):
    todo_id: int
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class TodoDeleted(Event, TodoEvent):
    todo_id: int
