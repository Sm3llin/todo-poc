from collections import defaultdict
from typing import List, DefaultDict, Set

from events import Event
from models.todo import Todo


class EventManager:
    subscriptions: DefaultDict[str, Set[object]] = defaultdict(set)

    @classmethod
    def subscribe(cls, topic, handler):
        if not hasattr(handler, "apply"):
            raise AttributeError("handler must implement apply method for event updates")
        cls.subscriptions[topic].add(handler)

    @classmethod
    def remove(cls, topic, handler):
        cls.subscriptions[topic].remove(handler)

    def play(self, topic: str, event: Event):
        subscriptions = self.subscriptions.get(topic, set())

        for subscription in subscriptions:
            subscription.apply(event)


class EventStore:
    events: List[Event] = []

    def __init__(self, topic: str, event_manager: EventManager, handler):
        self.em = event_manager
        self.topic = topic

        self.em.subscribe(self.topic, handler=handler)

    def push(self, event: Event):
        self.events.append(event)

    def push_and_play(self, event: Event):
        self.push(event)
        self.em.play(self.topic, event)


# Setup Managers
em = EventManager()

todo_store = EventStore("todo-stuff", event_manager=em, handler=Todo)
