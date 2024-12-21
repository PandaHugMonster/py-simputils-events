from abc import abstractmethod, ABCMeta

from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicRuntime import BasicRuntime


class GenericEvent(BasicEventDefinition):

	_name: str = None

	@property
	def name(self) -> str:
		return self._name

	def __init__(self, name: str, runtime: BasicRuntime | None = None):
		super().__init__(runtime)
		if name is not None:
			self._name = name
