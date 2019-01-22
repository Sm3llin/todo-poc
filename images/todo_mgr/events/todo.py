from dataclasses import dataclass

from events import Event


class TodoEvent:
    __topic__ = "todo-stuff"


@dataclass
class TodoCreated(Event, TodoEvent):
    todo_id: int
    title: str
    description: str = ""


@dataclass
class TodoDeleted(Event, TodoEvent):
    todo_id: int
