from flask_restplus import Namespace, Resource, fields

from db import session
from models.todo import Todo as TodoModel

api = Namespace('todo', description='Todo List management')

todo = api.model('Todo', {
    "id": fields.String(required=True, attribute="todo_id", description="The Todo identifier"),
    "title": fields.String(description="The Todo item title"),
    "description": fields.String(description="The Todo item description"),
})


todo_parser = api.parser()
todo_parser.add_argument('title', type=str, help='Title to display summarise the Todo', required=True)
todo_parser.add_argument('description', type=str, help='Brief description of Todo')


@api.route('/')
class TodoList(Resource):
    @api.doc('list_todos')
    @api.marshal_list_with(todo)
    def get(self):
        """List all todos"""
        return session.query(Todo).all()

    @api.doc("create_todo")
    @api.expect(todo_parser)
    @api.response(409, "Todo not created")
    @api.marshal_with(todo)
    def put(self):
        """Create a new Todo"""
        args = todo_parser.parse_args()

        _todo = TodoModel.create(**args)

        if _todo:
            return _todo
        api.abort(409, "unable to create Todo")


@api.route('/<id>')
@api.param('id', 'The todo identifier')
@api.response(404, 'Todo not found')
class Todo(Resource):
    @api.doc('get_todo')
    @api.marshal_with(todo)
    def get(self, id):
        """Fetch a todo given its identifier"""
        _todo = session.query(TodoModel).get(id)

        if _todo:
            return _todo
        api.abort(404, "Todo {} doesn't exist".format(id))
