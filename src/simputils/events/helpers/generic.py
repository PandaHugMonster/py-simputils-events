from collections.abc import Iterable

from simputils.events.abstract.AbstractDistributedAdapter import AbstractDistributedAdapter
from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.EventManager import EventManager
from simputils.events.runtimes.DistributedEventRuntime import DistributedEventRuntime


def create_distributed_event_manager(
	adapter: AbstractDistributedAdapter,
	*,
	runtime_kwargs: dict | None = None,
	additional_runtimes: Iterable[AbstractEventRuntime] | None = None,
):
	"""
	Create ready to use event-manager with distributed runtime and specific adapter

	Syntactic sugar, simplifies creation of ready to use event-manager
	with prepared and attached distributed runtime and specific adapter

	:param adapter:
	:param runtime_kwargs:
	:param additional_runtimes:
	:return:
	"""
	runtime_kwargs = runtime_kwargs if runtime_kwargs is not None else {}

	additional_runtimes = additional_runtimes if additional_runtimes is not None else []

	if adapter is None:
		raise Exception("Adapter could have not been instantiated.")

	# noinspection PyArgumentList
	runtime = DistributedEventRuntime(adapter, **runtime_kwargs)

	em = EventManager(runtimes=(runtime, *additional_runtimes)).init()

	return em