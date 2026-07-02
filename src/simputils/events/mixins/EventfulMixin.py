from typing import TYPE_CHECKING

from typing_extensions import Any

from simputils.events.abstract.AbstractEventRuntime import AbstractEventRuntime
from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.components.EventManager import EventManager
from simputils.events.types import EventType, EventCallType

if TYPE_CHECKING:
	from simputils.events.components.BasicEventResult import BasicEventResult


class EventfulMixin:
	"""
	Parent mixin class for simple utilizing simputils-events infrastructure.

	You always can implement your custom one, just follow the lead on this one
	when implementing custom one.

	For example if you don't like the naming or structure of this mixin - simply implement
	the custom one for your needs. Ideally, you shouldn't do that.

	Implementation of your own can make development across different projects more complicated.
	So, whenever possible - please use this one instead of the custom one.
	"""

	__event_manager: EventManager = None

	@property
	def event_manager(self) -> EventManager:
		if self.__event_manager is None:
			self.__event_manager = EventManager(back_ref_obj=self)
		return self.__event_manager

	@event_manager.setter
	def event_manager(self, value: EventManager):
		self.__event_manager = value

	def on(
		self,
		event: EventType,
		callback: EventCallType | None = None,
		**kwargs: Any
	) -> "BasicEvent":
		"""
		Registering an event

		:param event: Event name
		:param callback: Callback that could be triggered on this event
		:param kwargs: Custom kwargs for the callback
		:return:
		"""
		return self.event_manager.on_event(event, callback=callback, **kwargs)

	def trigger(
		self,
		event: EventType,
		*args,
		**kwargs
	)  -> "list[tuple[AbstractEventRuntime, BasicEventResult | None]]":
		"""
		Trigger an event

		It allows also additionally provide *args and **kwargs,
		those will be merged with those that assigned during event registration

		:param event: Event name
		:param args: Optional args for a callback
		:param kwargs: Optional kwargs for a callback
		:return: BasicEventResult (unless redefined) or None
		"""
		return self.event_manager.event_run(event, *args, **kwargs)
