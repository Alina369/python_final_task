from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class EventType(Enum):
    GAME_OVER = 'Ваше приключение закончилось... Прощайте!'


@dataclass
class Event:
    name: EventType
    action: Callable


class Events:
    @staticmethod
    def game_over_event():
        event_system.add(Event(EventType.GAME_OVER, lambda: (None, None)))


class EventSystem:
    def __init__(self):
        self.__queue = []

    def add(self, event: Event):
        self.__queue.append(event)

    def get_event(self) -> Optional[Event]:
        if self.__queue:
            return self.__queue.pop(0)


event_system = EventSystem()