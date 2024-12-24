from datetime import datetime, timezone


class SimpleEvent:

	_name: str = None
	_type: str | None = None
	_tags: str | None = None
	_data: dict | None = None

	_result_data: dict | None = None

	_created_at: datetime = None
	_processed_at: datetime = None

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
	def result_data(self) -> dict:
		return self._result_data

	@result_data.setter
	def result_data(self, val: dict):
		if self._processed_at is None:
			self._processed_at = datetime.now(timezone.utc)
		self._result_data = val

	def __str__(self):
		return (
			f'<{self.__class__.__name__} '
			f'name="{self.name}" '
			f'type="{self.type}" '
			f'tags="{self.tags}" '
			f'data="{self.data}">'
		)

	def __init__(
		self,
		name: str,
		data: dict = None,
		type: str = None,
		tags: str = None,
	):
		self._created_at = datetime.now(timezone.utc)
		self._name = name
		self._data = data
		self._type = type
		self._tags = tags
