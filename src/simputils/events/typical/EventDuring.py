from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.typical.TypicalEventEnum import TypicalEventEnum


class EventDuring(BasicEventDefinition):

	@property
	def name(self) -> str:
		return TypicalEventEnum.DURING
