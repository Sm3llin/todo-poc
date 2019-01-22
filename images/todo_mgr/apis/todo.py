from flask_restplus import Namespace, Resource, fields

from db import session
from models.todo import Todo as TodoModel

api = Namespace("todo", description="Todo List management")

todo = api.model("Todo", {
    "id": fields.String(required=True, attribute="todo_id", description="the Todo identifier"),
    "title": fields.String(description="the Todo item title"),
    "description": fields.String(description="the Todo item description"),
})


todo_parser = api.parser()
todo_parser.add_argument("title", type=str, help='title to display summarise the Todo', required=True)
todo_parser.add_argument("description", type=str, help='brief description of Todo')

update_parser = todo_parser.copy()
update_parser.replace_argument("title", type=str, help='title to display summarise the Todo', required=False)


@api.route('/')
class TodoList(Resource):
    @api.doc('list_todos')
    @api.marshal_list_with(todo)
    def get(self):
        """list all todos"""
        return session.query(TodoModel).all()

    @api.doc("create_todo")
    @api.expect(todo_parser)
    @api.response(409, "Todo not created")
    @api.marshal_with(todo)
    def post(self):
        """create a new Todo"""
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
        """fetch a todo given its identifier"""
        _todo = session.query(TodoModel).get(id)

        if _todo:
            return _todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    @api.doc('update_todo')
    @api.expect(update_parser)
    @api.response(200, "Todo updated")
    def put(self, id):
        """update a todo by its given identifier"""
        success = TodoModel.update(todo_id=id, **update_parser.parse_args())

        if success:
            return "", 200
        api.abort(404, "Todo {} doesn't exist".format(id))

    @api.doc('delete_todo')
    @api.response(200, "Todo deleted")
    def delete(self, id):
        """delete a todo by its given identifier"""
        success = TodoModel.delete(todo_id=id)

        if success:
            return "", 200
        api.abort(404, "Todo {} doesn't exist".format(id))
