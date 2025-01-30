from abc import ABCMeta, abstractmethod

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.auxiliary.RunnableObject import RunnableObject


class BasicEventHandler(RunnableObject, metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: SimpleEvent):
		pass  # pragma: no cover
