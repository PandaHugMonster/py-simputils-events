from simputils.events.generic.BasicTypicalEventDefinition import BasicTypicalEventDefinition


class EventBefore(BasicTypicalEventDefinition):

	def get_name(self) -> str:
		return "before"
