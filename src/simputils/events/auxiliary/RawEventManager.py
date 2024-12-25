import functools

from simputils.events.auxiliary.EventingMixin import EventingMixin
from simputils.events.generic.BasicRuntime import BasicRuntime


class RawEventManager(EventingMixin):
	"""
	Abstract event-manager class

	It can be used to build non-singleton event-managers (in the most cases discouraged)
	"""
	pass
