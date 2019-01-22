import json
import time

from db import Base, engine, session
from events import Event

from models.todo import Todo
from stores import todo_store


if __name__ == '__main__':
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
