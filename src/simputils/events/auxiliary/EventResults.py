from collections import OrderedDict
from threading import Event, Lock
from uuid import UUID

from simputils.events.SimpleEvent import SimpleEvent


class EventResults:

	STATUS_UNKNOWN = "unknown"
	STATUS_FAIL = "fail"
	STATUS_SUCCESS = "success"

	_event_uid: UUID = None
	_event_name: str = None

	_events: OrderedDict[str, SimpleEvent] = None

	_updated_lock: Lock = None
	_is_done_flag: Event = None

	@property
	def event_uid(self) -> UUID:
		return self._event_uid

	@property
	def status(self) -> str:
		if None in self._get_event_statuses():
			return self.STATUS_UNKNOWN
		return self.STATUS_SUCCESS if self else self.STATUS_FAIL

	@property
	def events(self) -> OrderedDict[str, SimpleEvent]:
		return self._events

	def __init__(self, event_uid: UUID, event_name: str):
		self._event_uid = event_uid
		self._event_name = event_name

		self._updated_lock = Lock()
		self._is_done_flag = Event()
		self._events = OrderedDict()

	def append(self, event: SimpleEvent, status: bool = None):
		self.set_status(event, status)

	def set_status(self, event: SimpleEvent, status: bool | None):
		uid = str(event.obj_uid)

		with self._updated_lock:
			if status is not None:
				event.status = status
			if uid not in self._events:
				self._events[uid] = event

			self._flag_control()

	def wait(self, timeout=None):
		if self._events:
			self._is_done_flag.wait(timeout)

		return self

	def _get_event_statuses(self):
		res = []
		for event in self.events.values():
			res.append(event.status)
		return res

	def _flag_control(self):
		if None in self._get_event_statuses():
			self._is_done_flag.clear()
		else:
			self._is_done_flag.set()

	def __bool__(self):
		return all(self._get_event_statuses())

	def __str__(self):  # pragma: no cover
		events_count = len(self._events)
		events_word = "event" if events_count == 1 else "events"
		return f"{self.status} ({events_count} {events_word})"
