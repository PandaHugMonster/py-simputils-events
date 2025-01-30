from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid1

if TYPE_CHECKING:  # pragma: no cover
	from simputils.events.types import EventHandlerType


class SimpleEvent:

	_event_uid: UUID = None
	_name: str = None

	_obj_uid: UUID = None

	_type: str | None = None
	_tags: str | None = None
	_data: dict | None = None

	_result: dict | None = None

	_created_at: datetime = None
	_processed_at: datetime = None
	_status: bool = None
	_priority: int = None

	_handler: "EventHandlerType" = None

	@property
	def handler(self) -> "EventHandlerType":
		return self._handler

	@property
	def priority(self) -> int:
		return self._priority

	@property
	def status(self) -> bool:
		return self._status

	@status.setter
	def status(self, val: bool):
		self._status = val

	@property
	def event_uid(self) -> UUID:
		return self._event_uid

	@property
	def obj_uid(self) -> UUID:
		return self._obj_uid

	@property
	def name(self) -> str:
		return self._name

	@property
	def type(self) -> str:
		return self._type

	@property
	def tags(self) -> str:
		return self._tags

	@property
	def data(self) -> dict:
		return self._data

	@property
	def created_at(self) -> datetime:
		return self._created_at

	@property
	def processed_at(self) -> datetime:
		return self._processed_at

	@processed_at.setter
	def processed_at(self, val: datetime):
		self._processed_at = val

	@property
	def result(self) -> dict:
		return self._result

	def set_result(self, val: dict):
		if self.processed_at is None:
			self.processed_at = datetime.now(timezone.utc)
		self._result = val

	def __str__(self):
		return (
			f'<{self.__class__.__name__} '
			f'name="{self.name}" '
			f'type="{self.type}" '
			f'tags="{self.tags}" '
			f'data="{self.data}" '
			f'status="{self.status}" '
			f'result="{self.result}" '
			f'created_at="{self.created_at}" '
			f'processed_at="{self.processed_at}" '
			f'handler="{self.handler.__name__}" '
			f'obj_uid="{self.obj_uid}" '
			f'event_uid="{self.event_uid}">'
		)

	def __repr__(self):
		status = ""
		processed_at = ""
		result = ""
		if self.status is not None:
			status = f" of status \"{self.status}\""
		if self.processed_at is not None:
			processed_at = f" processed at \"{self.processed_at}\""
		if self.result:
			result = f" with result \"{self.result}\""
		return f"Event \"{self.name}\"{status}{processed_at}{result}"

	# noinspection PyShadowingBuiltins
	def __init__(
		self,
		name: str,
		event_uid: UUID,
		handler: "EventHandlerType",
		data: dict = None,
		priority: int = 0,
		type: str = None,
		tags: str = None,
	):
		self._event_uid = event_uid
		self._obj_uid = uuid1()
		self._handler = handler
		self._created_at = datetime.now(timezone.utc)
		self._name = name
		self._data = data
		self._priority = priority
		self._type = type
		self._tags = tags
