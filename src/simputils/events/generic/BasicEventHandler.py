from abc import ABCMeta, abstractmethod

from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.RunnableObject import RunnableObject


class BasicEventHandler(RunnableObject, metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: SimpleEventingObj):
		pass  # pragma: no cover
