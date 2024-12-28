from threading import Thread
from typing import Callable

from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.EventsResult import EventsResult
from simputils.events.generic.BasicRuntime import BasicRuntime


class LocalParallelRuntime(BasicRuntime):

	threading_callback: type[Thread] | Callable = Thread

	def _sub_callback(self, event: SimpleEventingObj, callback: Callable, events_result: EventsResult):
		res = callback(event)
		events_result.set_status(event, res)

	def run(self, event: SimpleEventingObj, callback: Callable, events_result: EventsResult) -> bool | None:
		events_result.append(event)
		self.threading_callback(target=self._sub_callback, args=(event, callback, events_result)).start()
		return None
