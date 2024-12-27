import functools

from simputils.events.generic.BasicRuntime import BasicRuntime


def on_event(
	event_name: str | type,
	data: dict = None,
	priority: int = 0,
	type: str = None,
	tags: list[str] = None,
	runtime: type[BasicRuntime] | BasicRuntime = None
):
	"""
	Attaching event to methods of classes inherited from `BasicEventingObject

	:param event_name:
	:param data:
	:param priority:
	:param type:
	:param tags:
	:param runtime:
	:return:
	"""
	def decorator(func):
		func.decor_type = "simputils"
		func.decorated_with = on_event.__name__
		func.decorated_data = {
			"event_name": event_name,
			"data": data,
			"priority": priority,
			"type": type,
			"tags": tags,
			"runtime": runtime,
		}

		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)  # pragma: no cover
		return wrapper
	return decorator
