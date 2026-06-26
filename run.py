#!/bin/env python3
import logging
from uuid import uuid1, UUID

from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.modules.gcp.adapters.GooglePubSubAdapter import GooglePubSubAdapter
from simputils.events.mixins.EventfulMixin import EventfulMixin
from simputils.events.runtimes.DistributedEventRuntime import DistributedEventRuntime
from simputils.events.runtimes.LocalEventRuntime import LocalEventRuntime

# log_level = logging.DEBUG
log_level = logging.INFO

logging.basicConfig(level=log_level)


class MyObjClass(EventfulMixin):

	_data = None

	def __init__(self):
		self._data = {}
		super().__init__()

	def add_item(self, item):
		uid = uuid1()

		self.trigger("before-add-item", self._data, uid, item)
		self._data[uid] = item
		self.trigger("after-add-item", self._data, uid, item)

		return uid

	def del_item(self, uid: UUID):
		self.trigger("before-del-item", self._data, uid, self._data[uid])
		del self._data[uid]
		self.trigger("after-del-item", self._data, uid)

	def collapse_duplicates(self):
		sub_results = self.trigger("before-collapse-duplicates", self._data)

		existing_values_cache = []
		duplicates = []
		for k, v in self._data.items():
			if v in existing_values_cache:
				duplicates.append(k)
			else:
				existing_values_cache.append(v)

		for uid in duplicates:
			self.del_item(uid)

		self.trigger("after-collapse-duplicates", self._data)

	def __str__(self):
		return f"{self._data}"


if __name__ == "__main__":

	obj = MyObjClass()
	# obj.event_manager = create_distributed_event_manager(
	# 	GooglePubSubAdapter(topic=channel).init()
	# )

	subscription = "projects/experiments-497610/subscriptions/exp-events"
	topic = "projects/experiments-497610/topics/exp-events"

	pub_sub_adapter = GooglePubSubAdapter(topic=topic).init()
	pub_sub_adapter.create_topic(topic, exists_ok=True)

	runtimes = [
		# DummyEventRuntime(skip_invoke_callbacks=False),

		# DummyEventRuntime(skip_invoke_callbacks=True),
		LocalEventRuntime(),
		DistributedEventRuntime(pub_sub_adapter),
	]
	obj.event_manager.set_event_runtimes(*runtimes)

	deleted_extracts = {}

	def evented_already_exists(evt: BasicEventCall, data: dict, uid: UUID, item):
		if item in data.values():
			logging.info("Record \"%s\" already exists with UID: \"%s\"", item, uid)
			return False
		return True
	def evented_extract_deleted(evt: BasicEventCall, data: dict, uid: UUID, item):
		deleted_extracts[uid] = item
	def evented_log_deletion(evt: BasicEventCall, data: dict, uid: UUID, item):
		logging.warning("-- Deleting \"%s\" with UID \"%s\"", item, uid)

	obj.on("before-add-item", evented_already_exists)
	obj.on("before-del-item", evented_extract_deleted)
	obj.on("before-del-item", evented_log_deletion)

	obj.add_item("My name is PandaHugMonster")
	obj.add_item("I am 36 years old")
	obj.add_item("My name is PandaHugMonster")
	obj.add_item(22)
	obj.add_item(22.0)
	obj.add_item("22")
	obj.add_item(33)
	obj.add_item(33)
	obj.add_item(33)
	obj.add_item(True)
	obj.add_item(True)
	obj.add_item(False)

	logging.info("Deleted count: %i", len(deleted_extracts))
	obj.collapse_duplicates()
	logging.info("Deleted count: %i", len(deleted_extracts))
