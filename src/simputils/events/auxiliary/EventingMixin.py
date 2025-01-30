import functools
from copy import copy
from uuid import UUID

from simputils.events.auxiliary.AttachedEventHandler import AttachedEventHandler
from simputils.events.auxiliary.EventResults import EventResults
from simputils.events.auxiliary.helpers.eventing import is_permitted_by_params, check_permitted_events, \
	get_event_definition, add_event_handler, sort_pairs_by_priority, prepare_runtime
from simputils.events.exceptions.ActionMustBeConfirmed import ActionMustBeConfirmed
from simputils.events.generic.BasicEventingFoundation import BasicEventingFoundation
from simputils.events.generic.BasicEventRuntime import BasicEventRuntime
from simputils.events.runtimes.LocalSequentialRuntime import LocalSequentialEventRuntime
from simputils.events.types import EventRuntimeType, EventDefinitionType, EventHandlerType, EventRefType, \
	EventPriorityPair


class EventingMixin(BasicEventingFoundation):

	_default_runtime: EventRuntimeType = LocalSequentialEventRuntime()

	def get_permitted_events(self) -> list[EventDefinitionType] | list | None:
		return None

	# noinspection PyShadowingBuiltins
	def attach(
		self,
		event_name: EventRefType,
		handler: EventHandlerType,
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: list[str] = None,
		runtime: EventRuntimeType = None,
	):
		permitted_events = self.get_permitted_events()

		event_ref, event_name = get_event_definition(event_name)

		check_permitted_events(permitted_events, event_ref, event_name)

		attached_event_handler = self._prepare_attached_event_handler(
			event_ref,
			event_name,
			handler,
			type,
			runtime,
			data,
			tags,
			priority,
		)

		add_event_handler(self._attached_event_handlers, attached_event_handler)

	# noinspection PyShadowingBuiltins
	def _trigger_exec(
		self,
		events_result: EventResults,
		event_name: str,
		attached_handlers: list[AttachedEventHandler],
		event_uid: UUID,
		priority: int,
		type: str,
		tags: list[str],
		runtime: BasicEventRuntime,
		data: dict
	):
		event_uid = copy(event_uid)

		for aeh in attached_handlers:

			if not is_permitted_by_params(aeh, type, tags):
				continue

			merged_data = aeh.data or {}
			merged_data.update(copy(data) if data is not None else {})

			_type = aeh.event_type or type
			_tags = copy(aeh.event_tags or tags)

			current_runtime = prepare_runtime(
				aeh.runtime or runtime or self.default_runtime
			)

			event = self._generate_event_object(
				event_name,
				event_uid,
				aeh.handler,
				merged_data,
				priority,
				_type,
				_tags
			)

			# NOTE  Running the attached handler through the runtime
			status = current_runtime(event, aeh, events_result)

			if status is not None and not status:
				return False

		return True

	def _trigger_preprocess(self, event_name, target):
		res = []
		if event_name in target and target[event_name]:
			# noinspection PyTypeChecker
			res: list[EventPriorityPair] = sort_pairs_by_priority(
				target[event_name]
			)

		return res

	# noinspection PyShadowingBuiltins
	def trigger(
		self,
		event_name: EventRefType,
		data: dict = None,
		type: str = None,
		tags: list[str] = None,
		runtime: EventRuntimeType = None,
	) -> EventResults | None:
		event_uid = self._generate_event_uid()
		events_result = EventResults(event_uid, event_name)

		event_ref, event_name = get_event_definition(event_name)

		attached_event_handlers = self._trigger_preprocess(
			event_name,
			self._attached_event_handlers,
		)

		for priority, attached_handlers in attached_event_handlers:
			succeeded = self._trigger_exec(
				events_result,
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

		return events_result

	# noinspection PyShadowingBuiltins
	def on_event(
		self,
		event_name: EventRefType,
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: list[str] = None,
		runtime: EventRuntimeType = None
	):
		def decorator(func):

			self.attach(event_name, func, data, priority=priority, type=type, tags=tags, runtime=runtime)

			@functools.wraps(func)
			def wrapper(*args, **kwargs):
				return func(*args, **kwargs)  # pragma: no cover
			return wrapper

		return decorator

	def detach(self, event_name: EventRefType, confirm: bool = False):
		if confirm is not True:
			raise ActionMustBeConfirmed("\"Detaching event action\" must be explicitly confirmed")

		event_ref, event_name = get_event_definition(event_name)
		if event_name in self._attached_event_handlers:
			del self._attached_event_handlers[event_name]

	def detach_all(self, confirm: bool = False):
		if confirm is not True:
			raise ActionMustBeConfirmed("\"Detaching all events\" action must be explicitly confirmed")

		event_names = self.get_attached_events()
		for event_name in event_names:
			self.detach(event_name, confirm)

	def describe_event(
		self,
		event_name: EventRefType,
		data: dict = None,
		type: str = None,
		tags: list[str] = None,
		runtime: EventRuntimeType = None,
	):
		"""
		Describe event Chains
		:return:
		"""
		event_uid = self._generate_event_uid()
		event_ref, event_name = get_event_definition(event_name)

		attached_event_handlers = self._trigger_preprocess(
			event_name,
			self._attached_event_handlers,
		)

		res = []
		for priority, attached_handlers in attached_event_handlers:
			for aeh in attached_handlers:
				if not is_permitted_by_params(aeh, type, tags):
					continue

				merged_data = aeh.data or {}
				merged_data.update(copy(data) if data is not None else {})

				_type = aeh.event_type or type
				_tags = copy(aeh.event_tags or tags)

				# current_runtime = prepare_runtime(
				# 	aeh.runtime or runtime or self.default_runtime
				# )

				event = self._generate_event_object(
					event_name,
					event_uid,
					aeh.handler,
					merged_data,
					priority,
					_type,
					_tags
				)

				res.append(event)
		i = 1
		for event in res:
			print(f"{i}. ", event.handler.__name__)
			i += 1
