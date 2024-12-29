from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.EventResults import EventResults
from simputils.events.generic.BasicEventRuntime import BasicEventRuntime


class LocalSequentialEventRuntime(BasicEventRuntime):

	def run(self, event: SimpleEvent, callback: Callable, events_result: EventResults):
		res = callback(event)
		events_result.append(event, res)
		return res
