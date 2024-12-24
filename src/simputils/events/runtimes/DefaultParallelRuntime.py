from threading import Thread
from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.generic.BasicRuntime import BasicRuntime


class DefaultParallelRuntime(BasicRuntime):

	def run(self, event: SimpleEvent, callback: Callable):
		Thread(target=callback, args=(event, )).start()
