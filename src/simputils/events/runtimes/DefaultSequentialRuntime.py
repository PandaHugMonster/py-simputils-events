from enum import Enum
from typing import Callable

from simputils.events.generic.BasicRuntime import BasicRuntime


class DefaultSequentialRuntime(BasicRuntime):

	def run(self, event: str | Enum, callback: Callable, **kwargs):
		return callback(**kwargs)
