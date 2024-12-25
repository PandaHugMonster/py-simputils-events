from collections import OrderedDict
from threading import Event, Lock

from simputils.events.SimpleEvent import SimpleEvent


class EventsResult:

	STATUS_FAIL = "fail"
	STATUS_SUCCESS = "success"

	_events: OrderedDict[str, SimpleEvent] = None
	_results: OrderedDict[str, bool] = None

	_events_lock: Lock = None
	_results_lock: Lock = None

	_is_done_flag: Event = None

	@property
	def status(self):
		return self.STATUS_SUCCESS if self else self.STATUS_FAIL

	@property
	def events(self) -> OrderedDict[str, SimpleEvent]:
		return self._events

	@property
	def results(self) -> OrderedDict[str, bool]:
		return self._results

	def __init__(self):
		self._events_lock = Lock()
		self._results_lock = Lock()

		self._is_done_flag = Event()

		self._events = OrderedDict()
		self._results = OrderedDict()

	def append(self, event: SimpleEvent, result: bool = None):
		uid = str(event.uid)

		with self._events_lock:
			self._events[uid] = event

		self._set_result(uid, result)

	def set_result(self, event: SimpleEvent, result: bool):
		uid = str(event.uid)

		if uid not in self._events:
			with self._events_lock:
				self._events[uid] = event

		self._set_result(uid, result)

	def wait(self, timeout=None):
		self._is_done_flag.wait(timeout)

		return self

	def _set_result(self, uid: str, result: bool):
		with self._results_lock:
			self._results[uid] = result
			self._flag_control()

	def _flag_control(self):
		if None in self._results.values():
			self._is_done_flag.clear()
		else:
			self._is_done_flag.set()

	def __bool__(self):
		return all(self._results.values())

	def __str__(self):
		events_count = len(self._events)
		events_word = "event" if events_count == 1 else "events"
		return f"{self.status} ({events_count} {events_word})"
