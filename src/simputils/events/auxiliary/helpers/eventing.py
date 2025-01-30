import inspect
from typing import Any, OrderedDict

from simputils.events.auxiliary.AttachedEventHandler import AttachedEventHandler
from simputils.events.exceptions.NotPermittedEvent import NotPermittedEvent
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
import natsort

from simputils.events.generic.BasicEventRuntime import BasicEventRuntime


def is_permitted_by_params(handler: AttachedEventHandler, type: str, tags: list[str]) -> bool:
	if type and handler.event_type and handler.event_type != type:
		return False

	if type and handler.event_type is None:
		return False

	if tags and handler.event_tags and not all(tag in handler.event_tags for tag in tags):
		return False

	if tags and handler.event_tags is None:
		return False

	return True


def get_event_definition(
	event_name: str | type[BasicEventDefinition] | BasicEventDefinition
) -> tuple[BasicEventDefinition, str]:

	event_ref = None
	if not isinstance(event_name, str):
		if inspect.isclass(event_name) and issubclass(event_name, BasicEventDefinition):
			event_name = event_name()

		if isinstance(event_name, BasicEventDefinition):
			event_ref = event_name
			event_name = event_ref.get_name()

	return event_ref, event_name


def check_permitted_events(permitted_events, event_ref, event_name) -> True:
	if permitted_events is not None:

		if not permitted_events:
			raise NotPermittedEvent(
				"Eventing is forbidden on this object (\"permitted_events\" returned an empty list)"
			)

		perm_event_names = []
		for item in permitted_events:
			perm_event_ref, perm_event_name = get_event_definition(item)
			perm_event_names.append(perm_event_name)

		if event_name not in perm_event_names:
			raise NotPermittedEvent(
				f"Event \"{event_name}\" is not in the list of permitted: {perm_event_names}"
			)

	return True


def extract_priority_handler_pairs(group: list | dict) -> list[tuple[int, AttachedEventHandler]]:
	if isinstance(group, dict):
		group = group.items()
	group = list(group)

	res: list[tuple[int, AttachedEventHandler]] = []
	for index, sub_group in group:
		for item in sub_group:
			res.append(
				(index, item)
			)
	return res


def add_event_handler(
	target: dict | dict[str, dict] | dict[str, dict[str, list[AttachedEventHandler]]],
	attached_event_handler: AttachedEventHandler
):
	event_name = attached_event_handler.event_name
	priority = attached_event_handler.priority

	if event_name not in target:
		target[event_name] = {}

	if priority not in target[event_name]:
		target[event_name][priority] = []

	target[event_name][priority].append(attached_event_handler)


def _sort_by_priority_callback(item: list[str, AttachedEventHandler]):
	return int(item[0])


def sort_pairs_by_priority(pairs: list[list[str | int, Any]] | dict[str | int, Any]) -> OrderedDict[int, Any]:
	if isinstance(pairs, dict):
		pairs = pairs.items()
	pairs = list(pairs)

	# noinspection PyTypeChecker
	return natsort.natsorted(
		pairs,
		key=_sort_by_priority_callback,
		alg=natsort.ns.INT,
	)


def prepare_runtime(runtime: type[BasicEventRuntime] | BasicEventRuntime):
	if inspect.isclass(runtime):
		return runtime()
	return runtime
