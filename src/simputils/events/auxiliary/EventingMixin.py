import functools
from collections import OrderedDict
from copy import copy
from inspect import isclass
from typing import Callable
from uuid import uuid1, UUID

import natsort

from simputils.events.AttachedEventHandler import AttachedEventHandler
from simputils.events.SimpleEventObj import SimpleEventObj
from simputils.events.auxiliary.EventsResult import EventsResult
from simputils.events.exceptions.ActionMustBeConfirmed import ActionMustBeConfirmed
from simputils.events.exceptions.NotPermittedEvent import NotPermittedEvent
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicEventHandler import BasicEventHandler
from simputils.events.generic.BasicRuntime import BasicRuntime
from simputils.events.runtimes.LocalSequentialRuntime import LocalSequentialRuntime


class EventingMixin:

	default_runtime: type[BasicRuntime] | BasicRuntime = LocalSequentialRuntime()

	_mapped_runtimes: dict[str, type[BasicRuntime] | BasicRuntime] = None
	_attached_event_handlers: dict[str, OrderedDict[int, list[AttachedEventHandler]]] = None
	_events_result: EventsResult = None

	def get_permitted_events(self) -> list[BasicEventDefinition | type[BasicEventDefinition]] | list | None:
		return None

	def get_attached_events(self) -> list[str]:
		return natsort.natsorted(
			list(self._attached_event_handlers.keys())
		)

	def _sort_key_callback(self, item: list[str, AttachedEventHandler]):
		return int(item[0])

	def _sort_group(self, res):
		# noinspection PyTypeChecker
		return natsort.natsorted(
			res, key=self._sort_key_callback
		)

	def get_attached_event_handlers(self, event_name: str) -> list[AttachedEventHandler] | list:
		res = []
		if event_name in self._attached_event_handlers:
			for priority, attached_handlers in self._attached_event_handlers[event_name].items():
				for handler in attached_handlers:
					res.append(
						(priority, handler)
					)
		sub = self._sort_group(res)
		res = []
		for _, handler in sub:
			res.append(handler)
		return res

	def get_attached_event_priorities(self, event_name: str) -> OrderedDict[int, AttachedEventHandler]:
		res = OrderedDict()
		if event_name in self._attached_event_handlers:
			res.update(self._attached_event_handlers[event_name])

		res = self._sort_group(res.items())

		return res

	@property
	def results(self) -> EventsResult | None:
		return copy(self._events_result)

	def __init__(self, default_runtime: type[BasicRuntime] | BasicRuntime = None, *args, **kwargs):
		if default_runtime:
			self.default_runtime = default_runtime
		self._attached_event_handlers = {}

	def set_mapped_runtime(self, event_name: str, runtime: type[BasicRuntime] | BasicRuntime):
		if self._mapped_runtimes is None:
			self._mapped_runtimes = {}
		self._mapped_runtimes[event_name] = runtime

	def get_mapped_runtime(self, event_name: str):
		if event_name not in self._mapped_runtimes:
			return None
		return self._mapped_runtimes[event_name]

	def _get_event_definition(
		self,
		event_name: str | type[BasicEventDefinition] | BasicEventDefinition
	) -> tuple[BasicEventDefinition, str]:
		event_ref = None
		if not isinstance(event_name, str):
			if issubclass(event_name, BasicEventDefinition):
				event_name = event_name()
			if isinstance(event_name, BasicEventDefinition):
				event_ref = event_name
				event_name = event_ref.get_name()

		return event_ref, event_name

	def _check_permitted_events(self, event_ref, event_name) -> True:
		permitted_events = self.get_permitted_events()

		if permitted_events is not None:

			if not permitted_events:
				raise NotPermittedEvent(
					"Eventing is forbidden on this object (self.permitted_events() returned an empty list)"
				)

			perm_event_names = []
			for item in permitted_events:
				perm_event_ref, perm_event_name = self._get_event_definition(item)
				perm_event_names.append(perm_event_name)

			if event_name not in perm_event_names:
				raise NotPermittedEvent(
					f"Event \"{event_name}\" is not in the list of permitted: {perm_event_names}"
				)

		return True

	def attach(
		self,
		event_name: str | type,
		handler: BasicEventHandler | Callable,
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: list[str] = None,
		runtime: type[BasicRuntime] | BasicRuntime = None,
	):
		event_ref, event_name = self._get_event_definition(event_name)
		self._check_permitted_events(event_ref, event_name)

		if event_ref:
			type = event_ref.get_type() or type
			runtime = event_ref.get_runtime() or runtime

			sub_data = copy(event_ref.get_data() or {})
			sub_data.update(data or {})
			data = sub_data
			tags = copy((event_ref.get_tags() or []) + (tags or []))

		attached_event_handler = AttachedEventHandler(
			event_name=event_name,
			handler=handler,
			data=data,
			event_type=type,
			event_tags=tags,
			runtime=runtime,
		)
		if event_name not in self._attached_event_handlers:
			self._attached_event_handlers[event_name] = OrderedDict()
		if priority not in self._attached_event_handlers[event_name]:
			self._attached_event_handlers[event_name][priority] = []
		self._attached_event_handlers[event_name][priority].append(attached_event_handler)

	def _check_filter(self, aeh: AttachedEventHandler, type: str, tags: list[str]) -> bool:
		if type and aeh.event_type and aeh.event_type != type:
			return False

		if tags and aeh.event_tags and not all(tag in aeh.event_tags for tag in tags):
			return False

		return True

	def _generate_event_object(
		self,
		name: str,
		event_uid: UUID,
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: str = None
	) -> SimpleEventObj:
		return SimpleEventObj(
			name,
			event_uid,
			data,
			priority,
			type,
			tags
		)

	def _generate_event_uid(self) -> UUID:
		return uuid1()

	def _trigger_process_attached_event_handler(
		self,
		event_name: str,
		attached_handlers: list[AttachedEventHandler],
		event_uid: UUID,
		priority: int,
		type: str,
		tags: list[str],
		runtime: BasicRuntime,
		data: dict
	):
		for aeh in attached_handlers:
			if not self._check_filter(aeh, type, tags):
				continue

			merged_data = aeh.data or {}
			current_runtime = aeh.runtime or runtime or self.default_runtime
			if isclass(current_runtime):
				current_runtime = current_runtime()
			merged_data.update(data)

			aeh: AttachedEventHandler
			_type = aeh.event_type or type
			_tags = aeh.event_tags or tags
			event = self._generate_event_object(
				event_name,
				copy(event_uid),
				merged_data,
				priority,
				_type,
				copy(_tags)
			)

			status = current_runtime(event, aeh, self._events_result)

			if status is not None and not status:
				return False

		return True

	def trigger(
		self,
		event_name: str | type,
		data: dict = None,
		type: str = None,
		tags: list[str] = None,
		runtime: type[BasicRuntime] | BasicRuntime = None,
	) -> EventsResult | None:
		event_uid = self._generate_event_uid()
		self._events_result = EventsResult(event_uid)

		event_ref, event_name = self._get_event_definition(event_name)

		data = copy(data) if data is not None else {}

		if event_name in self._attached_event_handlers and self._attached_event_handlers[event_name]:
			attached_event_handlers = self._sort_group(
				self._attached_event_handlers[event_name].items()
			)
			for priority, attached_handlers in attached_event_handlers:
				succeeded = self._trigger_process_attached_event_handler(
					event_name,
					attached_handlers,
					event_uid,
					priority,
					type,
					tags,
					runtime,
					data,
				)

				if not succeeded:
					break

		return self._events_result
		# return None

	def on_event(
		self,
		event_name: str | type,
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: list[str] = None,
		runtime: type[BasicRuntime] | BasicRuntime = None
	):
		def decorator(func):

			self.attach(event_name, func, data, priority=priority, type=type, tags=tags, runtime=runtime)

			@functools.wraps(func)
			def wrapper(*args, **kwargs):
				return func(*args, **kwargs)  # pragma: no cover
			return wrapper

		return decorator

	def detach(self, event_name: str | type, confirm: bool = False):
		if not confirm:
			raise ActionMustBeConfirmed("\"Detaching event action\" must be explicitly confirmed")

		event_ref, event_name = self._get_event_definition(event_name)
		if event_name in self._attached_event_handlers:
			del self._attached_event_handlers[event_name]

	def detach_all(self, confirm: bool = False):
		if not confirm:
			raise ActionMustBeConfirmed("\"Detaching all events\" action must be explicitly confirmed")

		event_names = self.get_attached_events()
		for event_name in event_names:
			self.detach(event_name, confirm)
