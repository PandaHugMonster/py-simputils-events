from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from simputils.events.components.BasicEvent import BasicEvent
from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.components.BasicEventResult import BasicEventResult
from simputils.events.types import EventCallType

if TYPE_CHECKING:
	from simputils.events.components.EventManager import EventManager


class AbstractEventRuntime(metaclass=ABCMeta):

	@abstractmethod
	def event_registered(
		self,
		em: "EventManager",
		event: BasicEvent,
		callback: EventCallType | None,
		kwargs: dict | None = None
	):
		pass

	@abstractmethod
	def event_triggered(
		self,
		*,
		em: "EventManager",
		event: BasicEvent,
		events_result_class: type[BasicEventResult],
		event_call_class: type[BasicEventCall],
		args: list | tuple | None = None,
		kwargs: dict | None = None,
	) -> "BasicEventResult | None":
		pass
