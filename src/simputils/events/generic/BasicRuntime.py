from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.EventsResult import EventsResult


class BasicRuntime(metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: SimpleEventingObj, callback: Callable, events_result: EventsResult) -> bool | None:
		pass  # pragma: no cover

	def __call__(self, event: SimpleEventingObj, callback: Callable, events_result: EventsResult):
		return self.run(event, callback, events_result)
