from simputils.events.auxiliary.EventingMixin import EventingMixin


class RawEventManager(EventingMixin):
	"""
	Abstract event-manager class

	It can be used to build non-singleton event-managers (in the most cases discouraged)
	"""
	pass
