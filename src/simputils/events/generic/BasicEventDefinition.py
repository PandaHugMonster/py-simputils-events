import builtins
from abc import ABCMeta, abstractmethod

from simputils.events.generic.BasicEventRuntime import BasicEventRuntime


class BasicEventDefinition(metaclass=ABCMeta):

	_data: dict = None

	@abstractmethod
	def get_name(self) -> str:  # pragma: no cover
		pass

	def get_type(self) -> str | None:  # pragma: no cover
		return None

	def get_tags(self) -> list[str] | None:  # pragma: no cover
		return None

	def get_data(self) -> dict | None:  # pragma: no cover
		return None

	def get_runtime(self) -> builtins.type[BasicEventRuntime] | BasicEventRuntime | None:  # pragma: no cover
		return None

	def __init__(self, data: dict = None):  # pragma: no cover
		self._data = data

	def __str__(self):  # pragma: no cover
		return self.get_name()
