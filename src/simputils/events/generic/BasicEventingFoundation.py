import copy
import uuid

import natsort

from simputils.events.AttachedEventHandler import AttachedEventHandler
from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.helpers.eventing import prepare_runtime, extract_priority_handler_pairs, \
	sort_pairs_by_priority
from simputils.events.generic.BasicRuntime import BasicRuntime
from simputils.events.types import EventRuntimeType, EventPriorityPair, EventHandlerType


class BasicEventingFoundation:

	_default_runtime: EventRuntimeType = None

	_mapped_runtimes: dict[str, EventRuntimeType] = None
	_attached_event_handlers: dict[str, dict[int, list[AttachedEventHandler]]] = None

	@property
	def default_runtime(self) -> BasicRuntime:
		return self._default_runtime

	@default_runtime.setter
	def default_runtime(self, val: EventRuntimeType):
		self._default_runtime = prepare_runtime(val)

	def __init__(self, default_runtime: EventRuntimeType = None, *args, **kwargs):
		if default_runtime:
			self.default_runtime = default_runtime
		self._attached_event_handlers = {}

	def set_mapped_runtime(self, event_name: str, runtime: EventRuntimeType):
		if self._mapped_runtimes is None:
			self._mapped_runtimes = {}
		self._mapped_runtimes[event_name] = prepare_runtime(runtime)

	def get_mapped_runtime(self, event_name: str):
		if event_name not in self._mapped_runtimes:
			return None
		return self._mapped_runtimes[event_name]

	def get_attached_events(self) -> list[str]:
		res = []
		for item in self._attached_event_handlers.keys():
			res.append(item)
		return natsort.natsorted(res)

	def get_attached_event_handlers(self, event_name: str) -> list[AttachedEventHandler] | list:
		sub = []
		if event_name in self._attached_event_handlers:
			attached_event_handlers = self._attached_event_handlers[event_name]
			# noinspection PyTypeChecker
			sub = extract_priority_handler_pairs(attached_event_handlers)
		res = [h for _, h in sort_pairs_by_priority(sub)]
		return res

	def get_attached_event_priorities(self, event_name: str) -> EventPriorityPair:
		res = {}
		if event_name in self._attached_event_handlers:
			res.update(self._attached_event_handlers[event_name])

		res = sort_pairs_by_priority(res)

		return res

	# noinspection PyMethodMayBeStatic,PyShadowingBuiltins
	def _generate_event_object(
		self,
		name: str,
		event_uid: uuid.UUID,
		handler: EventHandlerType,
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: str = None
	) -> SimpleEventingObj:
		return SimpleEventingObj(
			name,
			event_uid,
			handler,
			data,
			priority,
			type,
			tags
		)

	# noinspection PyMethodMayBeStatic
	def _generate_event_uid(self) -> uuid.UUID:
		return uuid.uuid1()

	# noinspection PyMethodMayBeStatic,PyShadowingBuiltins
	def _prepare_attached_event_handler(
		self,
		event_ref,
		event_name,
		handler,
		type,
		runtime,
		data,
		tags,
		priority,
	):
		if event_ref:
			type = event_ref.get_type() or type
			runtime = prepare_runtime(event_ref.get_runtime() or runtime)

			sub_data = copy.copy(event_ref.get_data() or {})
			sub_data.update(data or {})
			data = sub_data
			tags = copy.copy((event_ref.get_tags() or []) + (tags or []))

		res = AttachedEventHandler(
			event_name=event_name,
			handler=handler,
			data=data,
			event_type=type,
			event_tags=tags,
			runtime=runtime,
			priority=priority,
		)

		return res
