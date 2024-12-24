import functools

from simputils.events.auxiliary.EventingMixin import EventingMixin
from simputils.events.generic.BasicRuntime import BasicRuntime


class RawEventManager(EventingMixin):
	"""
	Abstract event-manager class

	It can be used to build non-singleton event-managers (in the most cases discouraged)
	"""

	def on_event(
		self,
		event_name: str | type,
		data: dict = None,
		type: str = None,
		tags: list[str] = None,
		runtime: type[BasicRuntime] | BasicRuntime = None
	):
		def decorator(func):

			self.attach(event_name, func, data, type=type, tags=tags, runtime=runtime)

			@functools.wraps(func)
			def wrapper(*args, **kwargs):
				return func(*args, **kwargs)  # pragma: no cover
			return wrapper

		return decorator
