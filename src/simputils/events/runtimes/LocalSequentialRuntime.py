from typing import Callable

from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.EventsResult import EventsResult
from simputils.events.generic.BasicRuntime import BasicRuntime


class LocalSequentialRuntime(BasicRuntime):

	def run(self, event: SimpleEventingObj, callback: Callable, events_result: EventsResult):
		res = callback(event)
		events_result.append(event, res)
		return res
