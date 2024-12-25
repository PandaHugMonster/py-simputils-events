from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.EventsResult import EventsResult
from simputils.events.generic.BasicRuntime import BasicRuntime


class DefaultSequentialRuntime(BasicRuntime):

	def run(self, event: SimpleEvent, callback: Callable, events_result: EventsResult):
		res = self.normalize_return(
			callback(event)
		)
		events_result.append(event, res)
		return res
