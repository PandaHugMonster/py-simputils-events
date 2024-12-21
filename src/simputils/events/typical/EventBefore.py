from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.typical.TypicalEventEnum import TypicalEventEnum


class EventBefore(BasicEventDefinition):

	@property
	def name(self) -> str:
		return TypicalEventEnum.BEFORE
