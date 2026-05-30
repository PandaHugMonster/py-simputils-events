from collections.abc import Iterable

from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.EventManager import EventManager
from simputils.events.modules.distributed.DistributedEventRuntime import DistributedEventRuntime
from simputils.events.modules.distributed.adapters.GooglePubSubAdapter import GooglePubSubAdapter
from simputils.events.modules.distributed.enums.AdaptersEnum import AdaptersEnum


def create_distributed_event_manager(
	adapter_type: AdaptersEnum,
	*,
	prod_channel: str | None = None,
	sub_channel: str | None = None,
	runtime_kwargs: dict | None = None,
	additional_runtimes: Iterable[AbstractEventRuntime] | None = None,
):
	"""
	Create ready to use event-manager with distributed runtime and specific adapter

	Syntactic sugar, simplifies creation of ready to use event-manager
	with prepared and attached distributed runtime and specific adapter

	:param adapter_type:
	:param prod_channel:
	:param sub_channel:
	:param runtime_kwargs:
	:param additional_runtimes:
	:return:
	"""
	runtime_kwargs = runtime_kwargs if runtime_kwargs is not None else {}

	adapter = None
	if adapter_type == AdaptersEnum.GCP_PUB_SUB:
		adapter = GooglePubSubAdapter(
			topic=prod_channel,
			subscription=sub_channel,
		)

	additional_runtimes = additional_runtimes if additional_runtimes is not None else []

	if adapter is None:
		raise Exception("Adapter could have not been instantiated.")

	# noinspection PyArgumentList
	runtime = DistributedEventRuntime(adapter, **runtime_kwargs)

	em = EventManager(runtimes=(runtime, *additional_runtimes)).init()

	return em