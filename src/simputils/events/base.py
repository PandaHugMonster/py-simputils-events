import functools

from simputils.events.generic.BasicEventDefinition import BasicEventDefinition


def on_event(event: str | BasicEventDefinition, priority: int = 0):
	def decorator(func):
		func.lib_type = "simputils"
		func.event_attached = event
		func.event_priority = priority

		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)  # pragma: no cover
		return wrapper

	return decorator
