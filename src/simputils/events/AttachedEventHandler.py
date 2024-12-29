from copy import copy
from enum import Enum

from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.RunnableObject import RunnableObject
from simputils.events.generic.BasicEventHandler import BasicEventHandler
from simputils.events.generic.BasicRuntime import BasicRuntime


class AttachedEventHandler(RunnableObject):

	_event_name: str | Enum = None
	_event_type: str = None
	_event_tags: list[str] = None

	_handler: BasicEventHandler = None
	_data: dict = None

	_runtime: BasicRuntime = None
	_priority: int = None

	@property
	def priority(self) -> int:
		return self._priority

	@property
	def event_name(self) -> str:
		return self._event_name  # pragma: no cover

	@property
	def event_type(self) -> str | None:
		return self._event_type

	@property
	def event_tags(self) -> list[str] | None:
		return self._event_tags

	@property
	def handler(self) -> BasicEventHandler:
		return self._handler

	@property
	def data(self) -> dict | None:
		return copy(self._data)

	@property
	def runtime(self) -> BasicRuntime:
		return self._runtime

	def __init__(
		self,
		event_name: str | Enum,
		handler: BasicEventHandler,
		data: dict = None,
		event_type: str = None,
		event_tags: list[str] = None,
		runtime: BasicRuntime = None,
		priority: int = None,
	):
		self._event_name = event_name
		self._handler = handler
		self._data = data
		self._event_type = event_type
		self._event_tags = event_tags
		self._runtime = runtime
		self._priority = priority

	def run(self, event: SimpleEventingObj):
		# NOTE  Result from handler. Can be only: None, True, False, dict
		res = self._handler(event)

		if isinstance(res, dict):
			event.set_result(res)
			res = None

		if isinstance(res, bool):
			event.status = res

		if res is None and event.status is None:
			event.status = True

		return event.status
