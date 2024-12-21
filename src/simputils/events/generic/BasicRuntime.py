from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.events.generic.BasicEventDefinition import BasicEventDefinition


class BasicRuntime(metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: BasicEventDefinition, callback: Callable, **kwargs):
		pass  # pragma: no cover

	def __call__(self, event: BasicEventDefinition, callback: Callable, **kwargs):
		return self.run(event, callback, **kwargs)
