from threading import Thread
from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.EventsResult import EventsResult
from simputils.events.generic.BasicRuntime import BasicRuntime


class DefaultParallelRuntime(BasicRuntime):

	threading_callback: type[Thread] | Callable = Thread

	def _sub_callback(self, event: SimpleEvent, callback: Callable, events_result: EventsResult):
		res = self.normalize_return(
			callback(event)
		)
		events_result.set_result(event, res)

	def run(self, event: SimpleEvent, callback: Callable, events_result: EventsResult):
		events_result.append(event)
		self.threading_callback(target=self._sub_callback, args=(event, callback, events_result)).start()
