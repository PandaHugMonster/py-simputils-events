from threading import Thread
from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.EventResults import EventResults
from simputils.events.generic.BasicEventRuntime import BasicEventRuntime


class LocalParallelEventRuntime(BasicEventRuntime):

	threading_callback: type[Thread] | Callable = Thread

	def _sub_callback(self, event: SimpleEvent, callback: Callable, events_result: EventResults):
		res = callback(event)
		events_result.set_status(event, res)

	def run(self, event: SimpleEvent, callback: Callable, events_result: EventResults) -> bool | None:
		events_result.append(event)
		self.threading_callback(target=self._sub_callback, args=(event, callback, events_result)).start()
		return None
