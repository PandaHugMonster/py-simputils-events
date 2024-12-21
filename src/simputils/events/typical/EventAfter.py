from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.typical.TypicalEventEnum import TypicalEventEnum


class EventAfter(BasicEventDefinition):

	@property
	def name(self) -> str:
		return TypicalEventEnum.AFTER
