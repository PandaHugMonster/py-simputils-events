import inspect
from threading import Lock
from time import sleep
from uuid import UUID

import pytest

from simputils.SimpleEventManager import SimpleEventManager
from simputils.events.AttachedEventHandler import AttachedEventHandler
from simputils.events.SimpleEventingObj import SimpleEventingObj
from simputils.events.auxiliary.EventsResult import EventsResult
from simputils.events.base import on_event
from simputils.events.definitions.EventAfter import EventAfter
from simputils.events.exceptions.ActionMustBeConfirmed import ActionMustBeConfirmed
from simputils.events.exceptions.NotPermittedEvent import NotPermittedEvent
from simputils.events.generic.BasicEventingObject import BasicEventingObject
from simputils.events.runtimes.LocalParallelRuntime import LocalParallelRuntime
from simputils.events.runtimes.LocalSequentialRuntime import LocalSequentialRuntime

generic_lock = Lock()
resulting_list = []


class MyEventObj(BasicEventingObject):

	_type: str = None
	_permitted_events = None

	def __init__(self, type: str = None, permitted_events: list = None, *args, **kwargs):
		self._type = type
		self._permitted_events = permitted_events
		super().__init__(*args, **kwargs)

	def get_permitted_events(self):
		return self._permitted_events

	@on_event("setup-1", priority=1, type="type-1", tags=["tag-1", "tag-1.1"])
	def _handler_1(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)

	@on_event("setup-1", priority=2)
	def _handler_2(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return False

	@on_event("setup-1", priority=3)
	def _handler_3(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)

	#

	@on_event("setup-2", priority=4)
	def _handler_4(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return True

	@on_event("setup-2", priority=5)
	def _handler_5(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		event.status = False
		return True

	@on_event("setup-2", priority=6)
	def _handler_6(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		event.status = False

	#

	@on_event("setup-3", priority=7)
	def _handler_7(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		event.set_result({
			"result": "red",
		})

	@on_event("setup-3", priority=8)
	def _handler_8(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return {
			"result": "green",
		}

	@on_event("setup-3", priority=9)
	def _handler_9(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		event.set_result({
			"result": "violet",
		})

		return {
			"result": "blue",
		}

	@on_event("setup-3", priority=10)
	def _handler_10(self, event: SimpleEventingObj):
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		event.set_result({
			"result": "white",
		})
		return False

	#

	@on_event("setup-4", priority=11)
	def _handler_11(self, event: SimpleEventingObj):
		sleep(1)
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return {
			"result": "cyan",
		}

	@on_event("setup-4", priority=12)
	def _handler_12(self, event: SimpleEventingObj):
		sleep(1)
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return {
			"result": "magenta",
		}

	@on_event("setup-4", priority=13)
	def _handler_13(self, event: SimpleEventingObj):
		sleep(1)
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return {
			"result": "yellow",
		}

	@on_event("setup-4", priority=14)
	def _handler_14(self, event: SimpleEventingObj):
		sleep(1)
		handler_name = inspect.stack()[0][3]
		resulting_list.append(handler_name)
		return {
			"result": "black",
		}

	@on_event(EventAfter, priority=15)
	def _handler_after_1(self, event: SimpleEventingObj):
		return {
			"result": "AFTER 1",
		}

	@on_event(EventAfter(), priority=16)
	def _handler_after_2(self, event: SimpleEventingObj):
		return {
			"result": "AFTER 2",
		}


class TestGeneral:

	def test_attached_events_and_handlers(self):
		obj = MyEventObj()
		attached_events = obj.get_attached_events()
		assert set(attached_events) == {"setup-1", "setup-2", "setup-3", "setup-4", "after"}
		for event_name in attached_events:
			for aeh in obj.get_attached_event_handlers(event_name):
				if event_name == "setup-1":
					assert aeh.handler.__name__ in [
						"_handler_1",
						"_handler_2",
						"_handler_3",
					]
				if event_name == "setup-2":
					assert aeh.handler.__name__ in [
						"_handler_4",
						"_handler_5",
						"_handler_6",
					]
				if event_name == "setup-3":
					assert aeh.handler.__name__ in [
						"_handler_7",
						"_handler_8",
						"_handler_9",
						"_handler_10",
					]
				if event_name == "setup-4":
					assert aeh.handler.__name__ in [
						"_handler_11",
						"_handler_12",
						"_handler_13",
						"_handler_14",
					]
				if event_name == "after":
					assert aeh.handler.__name__ in [
						"_handler_after_1",
						"_handler_after_2",
					]

	def _sub_check_1(self, obj: MyEventObj):
		resulting_list.clear()

		res = obj.trigger("setup-1").wait(5)
		assert resulting_list == ["_handler_1", "_handler_2"]

		sub = list(res.events.values())

		event: SimpleEventingObj = sub[0]
		event1 = event
		assert event.name == "setup-1"
		assert event.status is True
		assert event.type == "type-1"
		assert event.tags == ["tag-1", "tag-1.1"]

		event: SimpleEventingObj = sub[1]
		event2 = event
		assert event.status is False

		assert str(event1.event_uid) == str(event2.event_uid)
		assert str(event1.obj_uid) != str(event2.obj_uid)

		assert event1.priority == 1
		assert event2.priority == 2

	def _sub_check_2(self, obj: MyEventObj):
		resulting_list.clear()

		res = obj.trigger("setup-2").wait(5)
		assert resulting_list == ["_handler_4", "_handler_5", "_handler_6"]

		sub = list(res.events.values())

		event: SimpleEventingObj = sub[0]
		assert event.status is True

		event: SimpleEventingObj = sub[1]
		assert event.status is True

		event: SimpleEventingObj = sub[2]
		assert event.status is False

	def _sub_check_3(self, obj: MyEventObj):
		resulting_list.clear()

		res = obj.trigger("setup-3").wait(5)
		assert resulting_list == [
			"_handler_7",
			"_handler_8",
			"_handler_9",
			"_handler_10",
		]

		sub = list(res.events.values())

		event: SimpleEventingObj = sub[0]
		assert event.status is True
		assert event.result == {"result": "red"}

		event: SimpleEventingObj = sub[1]
		assert event.status is True
		assert event.result == {"result": "green"}

		event: SimpleEventingObj = sub[2]
		assert event.status is True
		assert event.result == {"result": "blue"}

		event: SimpleEventingObj = sub[3]
		assert event.status is False
		assert event.result == {"result": "white"}

	def test_handler_behaviour(self):
		obj = MyEventObj()

		self._sub_check_1(obj)
		self._sub_check_2(obj)
		self._sub_check_3(obj)

	def _get_priority_and_handler_name(self, obj: MyEventObj, event_name: str, index: int) -> tuple[int, str]:
		priority, attached_events = obj.get_attached_event_priorities(event_name)[index]
		aeh: AttachedEventHandler = attached_events[0]
		return int(priority), str(aeh.handler.__name__)

	def test_attached_event_priorities(self):
		obj = MyEventObj()

		event_name = "setup-1"

		expected_index = 1
		priority, name = self._get_priority_and_handler_name(obj, event_name, 0)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 2
		priority, name = self._get_priority_and_handler_name(obj, event_name, 1)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 3
		priority, name = self._get_priority_and_handler_name(obj, event_name, 2)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		#

		event_name = "setup-2"

		expected_index = 4
		priority, name = self._get_priority_and_handler_name(obj, event_name, 0)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 5
		priority, name = self._get_priority_and_handler_name(obj, event_name, 1)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 6
		priority, name = self._get_priority_and_handler_name(obj, event_name, 2)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		#

		event_name = "setup-3"

		expected_index = 7
		priority, name = self._get_priority_and_handler_name(obj, event_name, 0)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 8
		priority, name = self._get_priority_and_handler_name(obj, event_name, 1)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 9
		priority, name = self._get_priority_and_handler_name(obj, event_name, 2)
		assert priority == expected_index and name == f"_handler_{expected_index}"

		expected_index = 10
		priority, name = self._get_priority_and_handler_name(obj, event_name, 3)
		assert priority == expected_index and name == f"_handler_{expected_index}"

	def test_check_non_permitted_events(self):

		obj = MyEventObj(permitted_events=["setup-1", "setup-2"], on_event_disabled=True)

		with pytest.raises(NotPermittedEvent):
			obj.attach("setup-3", obj._handler_10)

	def test_events_disallowed(self):

		obj = MyEventObj(permitted_events=[], on_event_disabled=True)

		with pytest.raises(NotPermittedEvent):
			obj.attach("setup-1", obj._handler_1)

	def test_event_manager_is_singleton(self):
		em1 = SimpleEventManager()
		em2 = SimpleEventManager()
		assert em1 is em2

	def test_event_manager_on_event_decorator(self):
		em = SimpleEventManager()

		@em.on_event("event-1")
		def handler_1(event: SimpleEventingObj):
			return {
				"result": "success",
				"name": handler_1.__name__,
			}

		@em.on_event("event-1")
		def handler_2(event: SimpleEventingObj):
			return {
				"result": "success",
				"name": handler_2.__name__,
			}

		@em.on_event("event-1")
		def handler_3(event: SimpleEventingObj):
			event.set_result({
				"result": "fail",
				"name": handler_3.__name__,
			})
			return False

		res = em.trigger("event-1").wait(5)

		sub = list(res.events.values())

		event: SimpleEventingObj = sub[0]
		assert event.status is True
		assert event.result == {
			"result": "success",
			"name": "handler_1",
		}

		event: SimpleEventingObj = sub[1]
		assert event.status is True
		assert event.result == {
			"result": "success",
			"name": "handler_2",
		}

		event: SimpleEventingObj = sub[2]
		assert event.status is False
		assert event.result == {
			"result": "fail",
			"name": "handler_3",
		}

	def test_parallel_events(self):
		obj = MyEventObj("parallel")
		obj.default_runtime = LocalParallelRuntime()

		res = obj.trigger("setup-4")

		for uid, event in res.events.items():
			assert event.status is None

		assert isinstance(res.event_uid, UUID)
		assert not res
		assert res.status == EventsResult.STATUS_UNKNOWN

		res.wait(5)

		for uid, event in res.events.items():
			assert event is not None

			assert event.result in (
				{"result": "magenta"},
				{"result": "black"},
				{"result": "cyan"},
				{"result": "yellow"},
			)

		assert res
		assert res.status == EventsResult.STATUS_SUCCESS

	def test_mixed_mapped_runtimes(self):
		obj = MyEventObj("parallel")
		obj.set_mapped_runtime("setup-4", LocalParallelRuntime())

		res_s4 = obj.trigger("setup-4")
		res_s1 = obj.trigger("setup-1")

		assert len(res_s1.events) == 2
		res_s4.wait(5)
		assert len(res_s4.events) == 4

	def test_runtime_checks(self):
		obj = MyEventObj("runtime-checks", default_runtime=LocalSequentialRuntime)

		obj.set_mapped_runtime("setup-4", LocalParallelRuntime())

		res = obj.get_mapped_runtime("goose")
		assert res is None

		res = obj.get_mapped_runtime("setup-4")
		assert isinstance(res, LocalParallelRuntime)

		res = obj.default_runtime
		assert isinstance(res, LocalSequentialRuntime)

		obj.default_runtime = LocalParallelRuntime
		res = obj.default_runtime
		assert isinstance(res, LocalParallelRuntime)

	def test_events_detachment(self):
		obj = MyEventObj("events-detachment")

		events = obj.get_attached_events()
		assert set(events) == {"setup-1", "setup-2", "setup-3", "setup-4", "after"}

		obj.detach("after", True)
		obj.detach("setup-1", True)
		obj.detach("setup-3", True)

		events = obj.get_attached_events()
		assert events == ["setup-2", "setup-4"]

		obj.detach_all(True)

		events = obj.get_attached_events()
		assert events == []

	def test_events_detachment_exception(self):
		obj = MyEventObj("events-detachment")

		with pytest.raises(ActionMustBeConfirmed):
			obj.detach("setup-1")

		with pytest.raises(ActionMustBeConfirmed):
			obj.detach_all()

	def test_simple_eventing_object(self):
		obj = MyEventObj("simple-eventing-object")

		res = obj.trigger(EventAfter)
		event: SimpleEventingObj = list(res.events.values())[0]

		event_str = str(event)
		event_repr = repr(event)

		assert isinstance(event_str, str)
		assert isinstance(event_repr, str)
