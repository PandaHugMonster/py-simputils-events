from typing import Any


class InterruptEventSequence(BaseException):

	_result: Any | None = None

	@property
	def result(self) -> Any | None:
		return self._result

	def __init__(self, result: Any | None = None):
		self._result = result
		super().__init__()
