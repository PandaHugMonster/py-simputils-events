import logging
from copy import copy
from typing import Callable
from uuid import UUID

from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.components.BasicEventResult import BasicEventResult
from simputils.events.components.EventManager import EventManager
from simputils.events.exceptions.InterruptEventSequence import InterruptEventSequence
from simputils.events.types import EventCallType


_logger = logging.getLogger(__name__)


class DummyEventRuntime(AbstractEventRuntime):

	_callbacks: dict[UUID, list[tuple[EventCallType, dict]]]
	_skip_invoke_callbacks: bool

	def __init__(self, skip_invoke_callbacks: bool = True):
		self._callbacks = {}
		self._skip_invoke_callbacks = skip_invoke_callbacks

	def event_registered(
		self, em: "EventManager",
		event: BasicEvent,
		callback: EventCallType | None,
		kwargs: dict | None = None
	):
		if event.uid not in self._callbacks:
			self._callbacks[event.uid] = []
		if callback is not None:
			self._callbacks[event.uid].append((callback, kwargs or {}))

	def event_triggered(
		self,
		*,
		em: "EventManager",
		event: BasicEvent,
		events_result_class: type[BasicEventResult],
		event_call_class: type[BasicEventCall],
		args: list | tuple | None = None,
		kwargs: dict | None = None
	) -> "BasicEventResult | None":

		callbacks = self._callbacks.get(event.uid)
		if not callbacks:
			callbacks = []

		_logger.debug(
			"Event \"%s\" Triggered with args: \"%s\" and kwargs: \"%s\". ",
			event, args, kwargs
		)
		if not self._skip_invoke_callbacks:
			call_results = []
			args = args or []
			for cbk, cbk_kwargs in callbacks:
				cbk_kwargs = copy(cbk_kwargs)
				cbk_kwargs.update(kwargs or {})

				event_call = event_call_class(event, cbk)
				try:
					call_res = event_call(*args, **cbk_kwargs)
					call_results.append((call_res, event_call))
				except InterruptEventSequence as e:
					event_call.set_interrupted(True)
					call_results.append((e.result, event_call))
					break
		else:
			call_results = None
			_logger.debug("Callbacks \"%s\" invoking is skipped.", callbacks)

		res = events_result_class()

		res.append({
			"em": em,
			"event": event,
			"events_result_class": events_result_class,
			"event_call_class": event_call_class,
			"args": args,
			"kwargs": kwargs,
			"callbacks": callbacks,
			"call_results": call_results,
			"skip_invoke_callbacks": self._skip_invoke_callbacks
		})

		return res
