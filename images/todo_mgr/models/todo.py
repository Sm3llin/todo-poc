import functools
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError

from db import Base, session
from events.todo import TodoCreated, TodoDeleted


class Todo(Base):
    __tablename__ = "todos"

    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    description = Column(String(1000))

    def __repr__(self):
        return f"<Todo todo_id={self.todo_id}>"

    @staticmethod
    def create(title: str, description: Optional[str] = None):
        todo = Todo(title=title, description=description)

        session.add(todo)

        try:
            session.commit()
        except IntegrityError:
            return None

        # Successfully able to create Todo, publish the event to the eventstore
        print(TodoCreated.publish(todo_id=todo.todo_id, title=todo.title, description=todo.description))
        return todo

    @staticmethod
    def delete(todo_id: int):
        if session.query(Todo).filter_by(todo_id=todo_id).delete():
            try:
                session.commit()
            except IntegrityError:
                return None

            print(TodoDeleted.publish(todo_id=todo_id))
            return
        else:
            raise ValueError

    @staticmethod
    @functools.singledispatch
    def apply(event):
        raise NotImplementedError()


@Todo.apply.register(TodoCreated)
def _(event: TodoCreated):
    todo = Todo(todo_id=event.todo_id, title=event.title, description=event.description)

    session.add(todo)

    return event


@Todo.apply.register(TodoDeleted)
def _(event: TodoDeleted):
    session.query(Todo).filter_by(todo_id=event.todo_id).delete()

    return event
