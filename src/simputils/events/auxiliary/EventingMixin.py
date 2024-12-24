from copy import copy
from inspect import isclass
from typing import Callable

from simputils.events.AttachedEventHandler import AttachedEventHandler
from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicEventHandler import BasicEventHandler
from simputils.events.generic.BasicRuntime import BasicRuntime
from simputils.events.runtimes.DefaultSequentialRuntime import DefaultSequentialRuntime


class EventingMixin:
	default_runtime: type[BasicRuntime] | BasicRuntime = DefaultSequentialRuntime()
	_mapped_runtimes: dict[str, type[BasicRuntime] | BasicRuntime] = None
	_attached_event_handlers: dict[str, list[AttachedEventHandler]] = None

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

	def attach(
		self,
		event_name: str | type,
		handler: BasicEventHandler | Callable,
		data: dict = None,
		type: str = None,
		tags: list[str] = None,
		runtime: type[BasicRuntime] | BasicRuntime = None,
	):
		event_ref = None
		if issubclass(event_name, BasicEventDefinition):
			event_name = event_name()
		if isinstance(event_name, BasicEventDefinition):
			event_ref = event_name

		if event_ref:
			event_name = event_ref.get_name()
			type = event_ref.get_type() or type
			runtime = event_ref.get_runtime() or runtime

			sub_data = event_ref.get_data() or {}
			sub_data.update(data or {})
			data = sub_data
			tags = (event_ref.get_tags() or []) + (tags or [])

		attached_event_handler = AttachedEventHandler(
			event_name=event_name,
			handler=handler,
			data=data,
			event_type=type,
			event_tags=tags,
			runtime=runtime,
		)
		if event_name not in self._attached_event_handlers:
			self._attached_event_handlers[event_name] = []
		self._attached_event_handlers[event_name].append(attached_event_handler)

	def _check_filter(self, aeh: AttachedEventHandler, type: str, tags: list[str]) -> bool:
		if type and aeh.event_type and aeh.event_type != type:
			return False

		if tags and aeh.event_tags and not all(tag in aeh.event_tags for tag in tags):
			return False

		return True

	def trigger(
		self,
		event_name: str | type,
		data: dict = None,
		type: str = None,
		tags: list[str] = None,
		runtime: type[BasicRuntime] | BasicRuntime = None,
	):
		event_chain_result = {}

		event_ref = None
		if issubclass(event_name, BasicEventDefinition):
			event_name = event_name()
		if isinstance(event_name, BasicEventDefinition):
			event_ref = event_name
			event_name = event_ref.get_name()

		data = copy(data) if data is not None else {}
		if event_name in self._attached_event_handlers:
			for aeh in self._attached_event_handlers[event_name]:
				if not self._check_filter(aeh, type, tags):
					continue

				merged_data = aeh.data or {}
				current_runtime = aeh.runtime or runtime or self.default_runtime
				if isclass(current_runtime):
					current_runtime = current_runtime()
				merged_data.update(data)

				event = SimpleEvent(event_name, merged_data, type, copy(tags))

				if aeh.event_name not in event_chain_result or (aeh.event_name in event_chain_result and event_chain_result[aeh.event_name]):

					sub_res = current_runtime.run(event, aeh)

					if sub_res is None:
						sub_res = True
					if not isinstance(sub_res, bool):
						raise Exception("Event handler can return only bool or None values")

					event_chain_result[aeh.event_name] = sub_res
