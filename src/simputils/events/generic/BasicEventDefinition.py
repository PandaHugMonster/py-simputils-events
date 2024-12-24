import builtins
from abc import ABCMeta, abstractmethod

from simputils.events.generic.BasicRuntime import BasicRuntime


class BasicEventDefinition(metaclass=ABCMeta):

	_data: dict = None

	@abstractmethod
	def get_name(self) -> str:
		pass

	def get_type(self) -> str | None:
		return None

	def get_tags(self) -> list[str] | None:
		return None

	def get_data(self) -> dict | None:
		return None

	def get_runtime(self) -> builtins.type[BasicRuntime] | BasicRuntime | None:
		return None

	def __init__(self, data: dict = None):
		self._data = data

	def __str__(self):
		return self.get_name()
