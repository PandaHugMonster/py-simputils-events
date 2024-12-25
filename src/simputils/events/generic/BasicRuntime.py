from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.EventsResult import EventsResult


class BasicRuntime(metaclass=ABCMeta):

	@classmethod
	def normalize_return(cls, value: bool | None) -> bool:
		if value is None:
			value = True
		if not isinstance(value, bool):
			raise Exception("Event handler can return only bool or None values")
		return value

	@abstractmethod
	def run(self, event: SimpleEvent, callback: Callable, events_result: EventsResult):
		pass  # pragma: no cover

	def __call__(self, event: SimpleEvent, callback: Callable, events_result: EventsResult):
		return self.run(event, callback, events_result)
