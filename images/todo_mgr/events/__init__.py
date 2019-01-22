import json
from typing import Dict, Type


class Event:
    event_map: Dict[str, "Type[Event]"] = {}

    def __init__(self, *args, **kwargs):
        pass

    def jsonify(self):
        return f'{{"type": "{self.__class__.__name__}", "payload": {json.dumps(self.__dict__)}}}'

    @classmethod
    def create(cls, message: Dict) -> "Event":
        event_type = message.get("type")
        event_payload = message.get("payload", {})

        if not event_type:
            raise ValueError("message does not contain a type unable to parse")
        elif not cls.event_map:
            cls.event_map = {e.__name__: e for e in cls.__subclasses__()}

            if not cls.event_map:
                raise ValueError("No configured events")

        return cls.event_map[event_type](**event_payload)

    @classmethod
    def publish(cls, *args, **kwargs) -> "Event":
        from stores import todo_store

        event = cls(*args, **kwargs)

        print("publishing event", event)
        todo_store.push(event)

        return event
