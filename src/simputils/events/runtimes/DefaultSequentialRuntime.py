from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.generic.BasicRuntime import BasicRuntime


class DefaultSequentialRuntime(BasicRuntime):

	def run(self, event: SimpleEvent, callback: Callable):
		return callback(event)
