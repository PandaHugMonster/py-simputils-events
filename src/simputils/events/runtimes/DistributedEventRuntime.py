import logging
from datetime import datetime, timezone
from uuid import UUID

from simputils.events.abstract.AbstractDistributedAdapter import AbstractDistributedAdapter
from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.components.BasicEventResult import BasicEventResult
from simputils.events.components.EventManager import EventManager
from simputils.events.types import EventCallType

_logger = logging.getLogger(__name__)


class DistributedEventRuntime(AbstractEventRuntime):

	_adapter: AbstractDistributedAdapter = None
	_callbacks: dict[UUID, list[tuple[EventCallType, dict]]] = None

	def __init__(self, adapter: AbstractDistributedAdapter):
		self._adapter = adapter
		self._callbacks = {}

	def event_registered(
		self,
		em: "EventManager",
		event: BasicEvent,
		callback: EventCallType | None,
		kwargs: dict | None = None
	):
		kwargs = {} if kwargs is None else kwargs

		if event.uid not in self._callbacks:
			self._callbacks[event.uid] = []

		if callback is not None:
			self._callbacks[event.uid].append((callback, kwargs))
			_logger.debug("Event \"%s\" registered with a callback \"%s\"", event, callback)
		else:
			_logger.debug("Event \"%s\" registered without callback", event)

	def event_triggered(
		self,
		*,
		em: "EventManager",
		event: BasicEvent,
		events_result_class: type[BasicEventResult],
		event_call_class: type[BasicEventCall],
		args: list | tuple | None = None,
		kwargs: dict | None = None
	) -> "BasicEventResult | None":
		channel = self._adapter.get_producer_channel()
		if channel is None:
			raise Exception("Channel for producer is None")
		data = {
			"uid": str(event.uid),
			"name": event.name,
			"ts": datetime.now(timezone.utc).isoformat()
		}
		self._adapter.produce(
			channel,
			data
		)

	def start(self):
		channel = self._adapter.get_consumer_channel()
		if channel is None:
			raise Exception("Channel for consumer is None")
		self._adapter.consume(channel, self._incoming_data)

	def _incoming_data(self, data: dict) -> bool:
		_logger.info("Data arrived: %s", data)
		event_name = data["name"]

		return True
