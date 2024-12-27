from abc import ABCMeta, abstractmethod

from simputils.events.SimpleEventObj import SimpleEventObj
from simputils.events.auxiliary.RunnableObject import RunnableObject


class BasicEventHandler(RunnableObject, metaclass=ABCMeta):

	@abstractmethod
	def run(self, event: SimpleEventObj):
		pass
