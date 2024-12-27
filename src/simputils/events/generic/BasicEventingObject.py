import inspect
from abc import ABCMeta, abstractmethod

from simputils.events.auxiliary.EventingMixin import EventingMixin
from simputils.events.base import on_event
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicRuntime import BasicRuntime


class BasicEventingObject(EventingMixin, metaclass=ABCMeta):

	@abstractmethod
	def get_permitted_events(self):
		pass  # pragma: no cover

	def __init__(
		self,
		default_runtime: type[BasicRuntime] | BasicRuntime = None,
		on_event_disabled: bool = False,
		*args,
		**kwargs
	):
		super().__init__(default_runtime, *args, **kwargs)

		if not on_event_disabled:
			for member_name in dir(self):
				data = self._on_event_check_and_prepare(member_name)
				if data is not None:
					self.attach(**data)

	def _on_event_check_and_prepare(self, member_name) -> dict | None:
		member = getattr(self, member_name)
		check = (
			inspect.ismethod(member)
			and "decor_type" in member.__dict__
			and member.__dict__["decor_type"] == "simputils"
			and member.__dict__["decorated_with"] == on_event.__name__
		)
		if check:
			data = member.__dict__["decorated_data"]
			data["handler"] = member
			if isinstance(data["event_name"], type):
				data["event_name"].runtime = data["event_name"]()
			if isinstance(data["event_name"], BasicEventDefinition):
				data["runtime"] = data["event_name"].get_runtime() or data["runtime"]

			return data

		return None
