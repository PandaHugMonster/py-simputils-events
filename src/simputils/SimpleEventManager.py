from simputils.events.auxiliary.RawEventManager import RawEventManager
from simputils.events.auxiliary.SingletonMeta import SingletonMeta


class SimpleEventManager(RawEventManager, metaclass=SingletonMeta):
	"""
	Singleton event-manager
	"""
	pass
