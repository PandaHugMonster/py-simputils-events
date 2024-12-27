from simputils.events.generic.BasicTypicalEventDefinition import BasicTypicalEventDefinition


class EventAfter(BasicTypicalEventDefinition):

	def get_name(self) -> str:
		return "after"
