import inspect
from abc import ABCMeta

from simputils.events.auxiliary.EventingMixin import EventingMixin
from simputils.events.base import on_event
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicRuntime import BasicRuntime


class BasicEventingObject(EventingMixin, metaclass=ABCMeta):

	def __init__(self, default_runtime: type[BasicRuntime] | BasicRuntime = None, *args, **kwargs):
		super().__init__(default_runtime, *args, **kwargs)

		member_names = dir(self)
		for member_name in member_names:
			member = getattr(self, member_name)
			if inspect.ismethod(member) and "decor_type" in member.__dict__ and member.__dict__["decor_type"] == "simputils" and member.__dict__["decorated_with"] == on_event.__name__:
				data = member.__dict__["decorated_data"]
				data["handler"] = member
				if isinstance(data["event_name"], type):
					data["event_name"].runtime = data["event_name"]()
				if isinstance(data["event_name"], BasicEventDefinition):
					data["runtime"] = data["event_name"].get_runtime() or data["runtime"]
				self.attach(**data)
