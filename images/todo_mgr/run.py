import json
import time

from flask import Flask

from apis import api
from db import Base, engine, session
from events import Event

from models.todo import Todo
from stores import todo_store


# Setup DB if required
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

events = [
    b'{"type": "TodoCreated", "payload": {"todo_id": 1, "title": "Finish the TodoList App", "description": ""}}',
    b'{"type": "TodoDeleted", "payload": {"todo_id": 1}}',
    b'{"type": "TodoCreated", "payload": {"todo_id": 2, "title": "Eat some dinner", "description": ""}}',
    b'{"type": "TodoCreated", "payload": {"todo_id": 3, "title": "Finished dinner, nom nom", "description": ""}}',
    b'{"type": "TodoCreated", "payload": {"todo_id": 4, "title": "another todo", "description": "hoping this makes a good todo description"}}',
    b'{"type": "TodoCreated", "payload": {"todo_id": 5, "title": "another todo", "description": "hoping this makes a good todo description"}}',
    b'{"type": "TodoDeleted", "payload": {"todo_id": 3}}',
    b'{"type": "TodoDeleted", "payload": {"todo_id": 2}}',
    b'{"type": "TodoDeleted", "payload": {"todo_id": 5}}',
]

for x in range(6, 4000):
    if x % 3 == 1:
        events.append(b'{"type": "TodoDeleted", "payload": {"todo_id": %d}}' % (x - 1))
    else:
        events.append(b'{"type": "TodoCreated", "payload": {"todo_id": %d, "title": "another todo"}}' % x)

events.append(b'{"type": "TodoModified", "payload": {"todo_id": 4, "title": "Another Todo"}}')
start = time.time()
count = 0
for event in events:
    todo_store.push_and_play(Event.create(json.loads(event)))

    if count % 500 == 0:
        session.commit()
    count += 1
else:
    session.commit()

elapsed = time.time() - start

print("=======================")
for event in todo_store.events:
    print(event.jsonify())
print("=======================")

print(session.query(Todo).all())

print(f"(catchup) time elapsed: {elapsed}, count: {count}")

Todo.update(41, description="this description does description things")

todo4 = session.query(Todo).get(4)
todo41 = session.query(Todo).get(41)

print(todo4, todo4.__dict__)
print(todo41, todo41.__dict__)

# Setup the webserver
app = Flask(__name__)
api.init_app(app)


if __name__ == '__main__':
    app.run(threaded=False, port=5001)
