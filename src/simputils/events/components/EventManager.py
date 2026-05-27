import logging
from collections.abc import Generator, Iterable
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from typing_extensions import Any

from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.runtimes.LocalEventRuntime import LocalEventRuntime
from simputils.events.exceptions.BasicEventException import BasicEventException
from simputils.events.exceptions.NoEventNameInferred import NoEventNameInferred
from simputils.events.types import EventType, EventCallType

if TYPE_CHECKING:
	from simputils.events.components.BasicEventCall import BasicEventCall
	from simputils.events.components.BasicEventResult import BasicEventResult


class EventManager:
	"""
	Standalone event-manager object, that usually automatically created per object,
	or can be created to be used without being attached to an object
	"""

	_runtimes: list[AbstractEventRuntime] = None

	_events_cache: dict[UUID, "BasicEvent"] = None
	_name_uid_map: dict[str, UUID] = None

	_back_ref_obj: object | None = None

	def __init__(
		self,
		*,
		runtimes: Iterable[AbstractEventRuntime] | None = None,
		back_ref_obj: object | None = None
	):
		self._back_ref_obj = back_ref_obj

		self._name_uid_map = {}
		self._events_cache = {}

		default_runtimes = [LocalEventRuntime(), ]
		runtimes = runtimes if runtimes else default_runtimes
		self.set_event_runtimes(*runtimes)

	def set_event_runtimes(
		self,
		*runtimes: AbstractEventRuntime,
	):
		if not runtimes:
			logging.warning("You are assigning empty list of runtimes. No runtimes will be used!")

		self._runtimes = list(runtimes) if runtimes is not None else []

	def _get_event(self, value: EventType | UUID) -> BasicEvent | None:
		if isinstance(value, BasicEvent):
			name = value.name
			uid = value.uid
		else:
			# noinspection PyStringConversionWithoutDunderMethod
			name = str(value.value if isinstance(value, Enum) else value)
			uid = self._name_uid_map.get(name)

		if not name:
			raise NoEventNameInferred(
				"Event name could not have been inferred. Provide event name instead of UID"
			)

		if uid is None or uid not in self._name_uid_map:
			event_class = self._get_event_class()
			event = event_class(name=name, uid=uid)
			self._events_cache[event.uid] = event
			self._name_uid_map[event.name] = event.uid
			return event

		return self._events_cache.get(uid, None)

	def on_event(
		self,
		event: EventType,
		callback: EventCallType | None = None,
		**kwargs: Any
	) -> "BasicEvent":
		"""
		Registering a callback on an event

		:param event: Event name
		:param callback: Callback that could be triggered on this event
		:param kwargs: Custom kwargs for the callback
		:return:
		"""
		event = self._get_event(event)
		if event is None:
			raise BasicEventException("Event could not have been found/created")

		for runtime in self._get_enabled_runtimes():
			runtime.event_registered(
				em=self,
				event=event,
				callback=callback,
				kwargs=kwargs,
			)

		return event

	def event_run(self, event: EventType, *args, **kwargs) -> "list[tuple[AbstractEventRuntime, BasicEventResult | None]]":
		"""
		Trigger an event

		It allows also additionally provide *args and **kwargs,
		those will be merged with those that assigned during event registration

		:param event: Event name
		:param args: Optional args for a callback
		:param kwargs: Optional kwargs for a callback
		:return: list[BasicEventResult | None] for each attached runtime
		"""
		event = self._get_event(event)
		if event is None:
			raise BasicEventException("Event could not have been found/created")

		res = []
		for runtime in self._get_enabled_runtimes():
			res.append((runtime, runtime.event_triggered(
				em=self,
				event=event,
				args=args,
				kwargs=kwargs,
				events_result_class=self._get_events_result_class(),
				event_call_class=self._get_event_call_class(),
			)))

		return res

	def _get_enabled_runtimes(self) -> Generator[AbstractEventRuntime]:
		for runtime in self._runtimes:
			# MARK  Implement potential filtering here
			yield runtime

	@classmethod
	def _get_event_class(cls) -> type["BasicEvent"]:
		"""
		Can be redefined with a custom `Event` class
		:return: Event class
		"""
		return BasicEvent

	@classmethod
	def _get_event_call_class(cls) -> type["BasicEventCall"]:
		"""
		Can be redefined with a custom `EventCall` class
		:return: EventCall class
		"""
		from simputils.events.components.BasicEventCall import BasicEventCall
		return BasicEventCall

	@classmethod
	def _get_events_result_class(cls) -> type["BasicEventResult"]:
		"""
		Can be redefined with a custom `EventResult` class
		:return: EventResult class
		"""
		from simputils.events.components.BasicEventResult import BasicEventResult
		return BasicEventResult
