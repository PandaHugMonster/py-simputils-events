import json
from collections.abc import Callable

from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1

from simputils.events.modules.distributed.abstract.AbstractDistributedAdapter import AbstractDistributedAdapter


class GooglePubSubAdapter(AbstractDistributedAdapter):

	_publisher = None
	_subscriber = None
	_topic: str | None = None
	_subscription: str | None = None

	def get_producer_channel(self) -> str | None:
		return self._topic

	def get_consumer_channel(self) -> str | None:
		return self._subscription

	def __init__(
		self,
		*,
		topic: str | None = None,
		subscription: str | None = None,
	):
		self._topic = topic
		self._subscription = subscription

		if not topic and not subscription:
			raise Exception(
				"Topic or Subscription names should be specified to enable publisher or subscriber"
			)

		self._publisher = pubsub_v1.PublisherClient() if topic and not subscription else None
		self._subscriber = pubsub_v1.SubscriberClient() if not topic and subscription else None

	def create_topic(self, name: str, exists_ok: bool = False):
		if self._publisher is None:
			raise Exception("Publisher is not enabled. Can't create topic")
		try:
			self._publisher.create_topic(name=name)
		except AlreadyExists as e:
			if not exists_ok:
				raise e

	def create_subscription(self, name: str, topic: str):
		if self._subscriber is None:
			raise Exception("Subscriber is not enabled. Can't create subscription")
		with self._subscriber as subscriber:
			subscriber.create_subscription(name=name, topic=topic)

	def produce(self, channel: str, data: dict, **kwargs):
		if self._publisher is None:
			raise Exception("Publisher is not enabled. Can't produce event")
		json_data = json.dumps(data).encode()
		future = self._publisher.publish(channel, json_data, **kwargs)
		future.result()

	def consume(self, channel: str, cbk: Callable):
		if self._subscriber is None:
			raise Exception("Subscriber is not enabled. Can't consume event")
		with self._subscriber as subscriber:
			future = subscriber.subscribe(
				channel,
				lambda msg: self._consumer_callback(msg, cbk)
			)
			future.result()

	def _consumer_callback(self, msg, runtime_callback: Callable | None = None):
		data: dict = json.loads(msg.data)

		if runtime_callback(data):
			msg.ack()
