from collections import OrderedDict
from threading import Event, Lock
from uuid import UUID

from simputils.events.SimpleEventObj import SimpleEventObj


class EventsResult:

	STATUS_FAIL = "fail"
	STATUS_SUCCESS = "success"

	_event_uid: UUID = None

	_events: OrderedDict[str, SimpleEventObj] = None
	_results: OrderedDict[str, bool] = None

	_events_lock: Lock = None
	_results_lock: Lock = None

	_is_done_flag: Event = None

	@property
	def event_uid(self) -> UUID:
		return self._event_uid

	@property
	def status(self) -> str:
		return self.STATUS_SUCCESS if self else self.STATUS_FAIL

	@property
	def events(self) -> OrderedDict[str, SimpleEventObj]:
		return self._events

	@property
	def results(self) -> OrderedDict[str, bool]:
		return self._results

	def __init__(self, event_uid: UUID):
		self._event_uid = event_uid
		self._events_lock = Lock()
		self._results_lock = Lock()

		self._is_done_flag = Event()

		self._events = OrderedDict()
		self._results = OrderedDict()

	def append(self, event: SimpleEventObj, result: bool = None):
		uid = str(event.obj_uid)

		with self._events_lock:
			self._events[uid] = event

		self._set_status(uid, result)

	def set_result(self, event: SimpleEventObj, result: bool):
		uid = str(event.obj_uid)

		if uid not in self._events:
			with self._events_lock:
				self._events[uid] = event

		self._set_status(uid, result)

	def wait(self, timeout=None):
		if self._events:
			self._is_done_flag.wait(timeout)

		return self

	def _set_status(self, uid: str, result: bool):
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
