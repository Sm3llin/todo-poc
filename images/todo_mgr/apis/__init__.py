from flask_restplus import Api

from .todo import api as todo_ns

api = Api(
    title="Todo Service",
    version="1.0",
    description="Endpoints for managing interactions with Todo's",
)

api.add_namespace(todo_ns)
