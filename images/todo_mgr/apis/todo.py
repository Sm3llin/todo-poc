from flask_restplus import Namespace, Resource, fields

from db import session
from models.todo import Todo

api = Namespace('todos', description='Todo List management')

todo = api.model('Todo', {
    "id": fields.String(required=True, attribute="todo_id", description="The Todo identifier"),
    "title": fields.String(description="The Todo item title"),
    "description": fields.String(description="The Todo item description"),
})


@api.route('/')
class TodoList(Resource):
    @api.doc('list_todos')
    @api.marshal_list_with(todo)
    def get(self):
        """List all todos"""
        return session.query(Todo).all()


@api.route('/<id>')
@api.param('id', 'The todo identifier')
@api.response(404, 'Todo not found')
class Todo(Resource):
    @api.doc('get_todo')
    @api.marshal_with(todo)
    def get(self, id):
        """Fetch a todo given its identifier"""
        _todo = session.query(Todo).get(id)

        if _todo:
            return _todo
        api.abort(404, "Todo {} doesn't exist".format(id))
