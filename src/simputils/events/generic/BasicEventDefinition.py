from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
	# noinspection PyUnresolvedReferences
	from simputils.events.generic.BasicRuntime import BasicRuntime


class BasicEventDefinition(metaclass=ABCMeta):

	_runtime: "BasicRuntime | None" = None

	@property
	@abstractmethod
	def name(self) -> str:
		pass  # pragma: no cover

	@property
	def runtime(self) -> "BasicRuntime | None":
		return self._runtime

	def __str__(self):
		return self.name

	def __init__(self, runtime: "BasicRuntime | None" = None):
		if runtime is not None:
			self._runtime = runtime
