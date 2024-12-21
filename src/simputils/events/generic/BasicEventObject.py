import inspect
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Callable

from simputils.events.AttachedEventCallback import AttachedEventCallback
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicRuntime import BasicRuntime
from simputils.events.runtimes.DefaultSequentialRuntime import DefaultSequentialRuntime


class BasicEventObject(metaclass=ABCMeta):
	default_runtime: BasicRuntime = DefaultSequentialRuntime()
	_mapped_runtimes: dict[str, BasicRuntime] = None

	_attached_events: dict[str, list[Callable]] = None

	@property
	@abstractmethod
	def defined_events(self) -> list[BasicEventDefinition]:
		pass

	@property
	def attached_events(self) -> dict[str, list[Callable]]:
		return self._attached_events

	@classmethod
	def set_mapped_runtime_for_class(cls, event: str | Enum, runtime: BasicRuntime):
		if cls._mapped_runtimes is None:
			cls._mapped_runtimes = {}
		cls._mapped_runtimes[event] = runtime

	def set_mapped_runtime_for_obj(self, event: str | Enum, runtime: BasicRuntime):
		if self._mapped_runtimes is None:
			self._mapped_runtimes = {}
		self._mapped_runtimes[event] = runtime

	def __init__(self):
		self._attached_events = {}
		all_list = dir(self)
		for item in all_list:
			method = getattr(self, item)
			if inspect.ismethod(method) and "__wrapped__" in method.__dict__:
				data = method.__dict__
				callback = data["__wrapped__"]

				if data["lib_type"] == "simputils":
					self.attach(data["event_attached"], callback, self)
		self.init()

	def init(self):
		pass

	def attach(self, event: str | Enum, callback: Callable | list[Callable], *args, **kwargs):
		defined_event = {}
		for item in self.defined_events:
			defined_event[item.name] = item
		if self.defined_events is not None and event not in defined_event:
			raise Exception(f"{event} is not part of permitted events {defined_event}")

		if event not in self._attached_events or not isinstance(self._attached_events[event], list):
			self._attached_events[event] = []

		if not isinstance(callback, list):
			callback = [callback]

		for item in callback:
			self._attached_events[event].append(
				AttachedEventCallback(
					event,
					item,
					*args,
					**kwargs
				)
			)

	def trigger(self, event: str | BasicEventDefinition, **kwargs):
		defined_event = {}
		for item in self.defined_events:
			defined_event[item.name] = item

		if isinstance(event, BasicEventDefinition):
			event_name = event.name
		else:
			event_name = str(event)
			event = defined_event[event_name]

		if event_name in self._attached_events:
			runtime = event.runtime if event.runtime is not None else self.default_runtime
			if self._mapped_runtimes and event_name in self._mapped_runtimes:
				runtime = self._mapped_runtimes[event_name]

			callbacks = self._attached_events[event_name]
			for callback in callbacks:
				res = runtime(event, callback, **kwargs)
				if res is False:
					break
