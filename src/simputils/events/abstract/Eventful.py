from abc import ABCMeta
from enum import Enum
from typing import Callable
from uuid import UUID, uuid1

from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.exceptions.InterruptEventSequence import InterruptEventSequence
from simputils.events.types import EventType


class Eventful(metaclass=ABCMeta):

	_event_callbacks: dict[str, dict[UUID, tuple[Callable, dict]]] = None
	_events_cache_uid: dict[UUID, BasicEvent] = None
	_events_cache_name: dict[str, BasicEvent] = None

	def __init__(self):
		self._event_callbacks = {}
		self._events_cache_uid = {}
		self._events_cache_name = {}

	@classmethod
	def __get_str_event(cls, event: EventType):
		if isinstance(event, Enum):
			return event.value
		return f"{event}"

	def event_register(self, event: EventType, callback: Callable, **kwargs):
		if not isinstance(event, BasicEvent):
			event = BasicEvent(self.__get_str_event(event))
		if event.name not in self._event_callbacks:
			self._event_callbacks[event.name] = {}
		self._events_cache_uid[event.uid] = event
		self._events_cache_name[event.name] = event
		self._event_callbacks[event.name][event.uid] = (callback, kwargs)
		return event

	def event_delete(self, uid: UUID):
		if uid in self._events_cache_uid:
			event = self._events_cache_uid[uid]
			del self._event_callbacks[event.name][uid]
			del self._events_cache_uid[uid]

	def event_purge(self, event: EventType):
		event = self.__get_str_event(event)
		if event in self._event_callbacks and self._event_callbacks[event]:
			for uid, callbacks in self._event_callbacks[event].items():
				del self._events_cache_uid[uid]
			del self._event_callbacks[event]

	def event_purge_all(self):
		self._event_callbacks = {}
		self._events_cache_uid = {}

	def event_trigger(self, event: EventType, *args, **kwargs):
		event = self.__get_str_event(event)
		if event not in self._events_cache_name:
			return

		event = self._events_cache_name[event]

		if event.name in self._event_callbacks and self._event_callbacks[event.name]:
			for uid, callback_group in self._event_callbacks[event.name].items():
				callback, callback_kwargs = callback_group
				callback_kwargs.update(kwargs)
				try:
					callback(event, *args, **callback_kwargs)
				except InterruptEventSequence as e:
					break
