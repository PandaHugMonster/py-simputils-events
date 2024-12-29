from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.EventResults import EventResults


class BasicEventRuntime(metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: SimpleEvent, callback: Callable, events_result: EventResults) -> bool | None:
		pass  # pragma: no cover

	def __call__(self, event: SimpleEvent, callback: Callable, events_result: EventResults):
		return self.run(event, callback, events_result)
