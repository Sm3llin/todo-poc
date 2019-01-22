import functools
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError

from db import Base, session
from events.todo import TodoCreated, TodoDeleted, TodoModified


def method_dispatch(func):
    # wrap the function with a dispatcher
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[0].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


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
                return False

            return TodoDeleted.publish(todo_id=todo_id) is not None
        else:
            return False

    @staticmethod
    def update(todo_id: int, title: Optional[str] = None, description: Optional[str] = None):
        update = {}

        if title:
            update[Todo.title] = title
        if description:
            update[Todo.description] = description

        if session.query(Todo).filter_by(todo_id=todo_id).update(update):
            try:
                session.commit()
            except IntegrityError:
                return False

            return TodoModified.publish(todo_id, title=title, description=description) is not None
        return False

    @method_dispatch
    def apply(_):
        raise NotImplementedError()

    @staticmethod
    @apply.register(TodoCreated)
    def _(event: TodoCreated):
        todo = Todo(todo_id=event.todo_id, title=event.title, description=event.description)

        session.add(todo)

        return event

    @staticmethod
    @apply.register(TodoDeleted)
    def _(event: TodoDeleted):
        session.query(Todo).filter_by(todo_id=event.todo_id).delete()

        return event

    @staticmethod
    @apply.register(TodoModified)
    def _(event: TodoModified):
        update = {}

        if event.title:
            update[Todo.title] = event.title
        if event.description:
            update[Todo.description] = event.description

        session.query(Todo).filter_by(todo_id=event.todo_id).update(update)

        return event
