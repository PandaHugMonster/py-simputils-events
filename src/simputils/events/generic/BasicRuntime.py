from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.events.SimpleEvent import SimpleEvent


class BasicRuntime(metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: SimpleEvent, callback: Callable):
		pass  # pragma: no cover

	def __call__(self, event: SimpleEvent, callback: Callable):
		return self.run(event, callback)
