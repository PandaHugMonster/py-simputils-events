from abc import ABCMeta, abstractmethod
from collections.abc import Callable


class AbstractDistributedAdapter(metaclass=ABCMeta):

	@abstractmethod
	def produce(self, channel: str, data: dict, **kwargs):
		pass

	@abstractmethod
	def consume(self, channel: str, cbk: Callable):
		pass

	@abstractmethod
	def get_producer_channel(self) -> str | None:
		pass

	@abstractmethod
	def get_consumer_channel(self) -> str | None:
		pass
