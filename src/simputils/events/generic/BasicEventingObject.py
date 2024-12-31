import inspect
from abc import ABCMeta, abstractmethod
from inspect import isfunction

from simputils.events.auxiliary.EventingMixin import EventingMixin
from simputils.events.base import on_event
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicEventRuntime import BasicEventRuntime


class BasicEventingObject(EventingMixin, metaclass=ABCMeta):

	@abstractmethod
	def get_permitted_events(self):
		pass  # pragma: no cover

	def __init__(
		self,
		default_runtime: type[BasicEventRuntime] | BasicEventRuntime = None,
		on_event_disabled: bool = False,
		*args,
		**kwargs
	):
		super().__init__(default_runtime, *args, **kwargs)

		if not on_event_disabled:
			for member_name in dir(self):
				member = getattr(self, member_name)
				if hasattr(member, "simputils_events"):
					# print(member.simputils_events)
					for data in member.simputils_events:
						self._attach_event(member, data)
				# check = (
				# 	inspect.ismethod(member)
				# 	and "decor_type" in member.__dict__
				# 	and member.__dict__["decor_type"] == "simputils"
				# 	and member.__dict__["decorated_events"]
				# )
				# if not check:
				# 	continue
				# decorated_events = member.__dict__["decorated_events"]
				# for data in decorated_events:
				# 	self._attach_event(member, data)

	def _attach_event(self, member, data):
		data["handler"] = member

		if isinstance(data["event_name"], type):
			data["event_name"].runtime = data["event_name"]()
		if isinstance(data["event_name"], BasicEventDefinition):
			data["runtime"] = data["event_name"].get_runtime() or data["runtime"]

		self.attach(**data)
