import inspect
from threading import Lock, Thread

from simputils.events.GenericEvent import GenericEvent
from simputils.events.base import on_event
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicEventObject import BasicEventObject
from simputils.events.runtimes.DefaultParallelRuntime import DefaultParallelRuntime
from simputils.events.runtimes.DefaultSequentialRuntime import DefaultSequentialRuntime

generic_lock = Lock()
resulting_list = []


class MyEventObj(BasicEventObject):

	EVENT_BEFORE = "before"
	EVENT_DURING = "during"
	EVENT_AFTER = "after"

	_type: str = None

	def __init__(self, type: str = None):
		self._type = type
		super().__init__()

	@property
	def defined_events(self) -> list[BasicEventDefinition]:
		return [
			GenericEvent(self.EVENT_BEFORE),
			GenericEvent(self.EVENT_DURING),
			GenericEvent(self.EVENT_AFTER),
		]

	def run(self):
		self.trigger(MyEventObj.EVENT_BEFORE)
		self.trigger(MyEventObj.EVENT_DURING)
		self.trigger(MyEventObj.EVENT_AFTER)

	@on_event(EVENT_BEFORE)
	def my_before_func1(self):
		resulting_list.append(inspect.stack()[0][3])

	@on_event(EVENT_BEFORE)
	def my_before_func2(self):
		resulting_list.append(inspect.stack()[0][3])

	@on_event(EVENT_DURING)
	def my_during_func1(self):
		resulting_list.append(inspect.stack()[0][3])

	@on_event(EVENT_AFTER)
	def my_after_func1(self):
		resulting_list.append(inspect.stack()[0][3])


class TestGeneral:

	def test_default_runtime(self):
		obj = MyEventObj()
		obj.run()

		assert resulting_list == ["my_before_func1", "my_before_func2", "my_during_func1", "my_after_func1"]
		resulting_list.clear()

	def test_parallel_runtime(self):
		MyEventObj.default_runtime = DefaultParallelRuntime()

		obj = MyEventObj("parallel")

		generic_lock.acquire(timeout=40)
		Thread(target=obj.run).start()
		generic_lock.acquire(timeout=1)

		assert len(resulting_list) == 4
		for item in ["my_before_func1", "my_before_func2", "my_during_func1", "my_after_func1"]:
			assert item in resulting_list

		generic_lock.release()
		resulting_list.clear()

	def test_generic_event_definition(self):
		event = GenericEvent("my-event", DefaultSequentialRuntime())

		assert str(event) == "my-event"
		assert isinstance(event.runtime, DefaultSequentialRuntime)

