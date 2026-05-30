import logging
from copy import copy
from typing import TYPE_CHECKING
from uuid import UUID

from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.components.BasicEventResult import BasicEventResult
from simputils.events.exceptions.InterruptEventSequence import InterruptEventSequence
from simputils.events.types import EventCallType

if TYPE_CHECKING:
	from simputils.events.components.EventManager import EventManager


_logger = logging.getLogger(__name__)


class LocalEventRuntime(AbstractEventRuntime):

	_event_callbacks: dict[UUID, list[tuple[EventCallType, dict]]] = None

	def __init__(self):
		self._event_callbacks = {}

	def event_registered(
		self,
		em: "EventManager",
		event: BasicEvent,
		callback: EventCallType,
		kwargs: dict | None = None
	):
		kwargs = {} if kwargs is None else kwargs

		if event.uid not in self._event_callbacks:
			self._event_callbacks[event.uid] = []

		if callback is not None:
			self._event_callbacks[event.uid].append((callback, kwargs))
			_logger.debug("Event \"%s\" registered with a callback \"%s\"", event, callback)
		else:
			_logger.debug("Event \"%s\" registered without callback", event)

	def event_triggered(
		self,
		*,
		em: "EventManager",
		event: BasicEvent,
		events_result_class: type[BasicEventResult],
		event_call_class: type[BasicEventCall],
		args: list | tuple | None = None,
		kwargs: dict | None = None,
	) -> "BasicEventResult | None":
		callbacks = self._event_callbacks.get(event.uid)
		if callbacks is None:
			return None

		args = args or []

		result = events_result_class()

		for cbk, cbk_kwargs in callbacks:
			cbk_kwargs = copy(cbk_kwargs)
			cbk_kwargs.update(kwargs or {})

			event_call = event_call_class(event, cbk)
			try:
				call_res = event_call(*args, **cbk_kwargs)
				_logger.debug("Event \"%s\" triggered a callback \"%s\"", event, cbk)
				result.append(call_res, event_call)
			except InterruptEventSequence as e:
				event_call.set_interrupted(True)
				result.append(e.result, event_call)
				break

		return result
