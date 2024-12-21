from threading import Thread
from typing import Callable

from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicRuntime import BasicRuntime


class DefaultParallelRuntime(BasicRuntime):

	def run(self, event: BasicEventDefinition, callback: Callable, **kwargs):
		Thread(target=callback, kwargs=kwargs).start()
