from enum import Enum


class TypicalEventEnum(Enum, str):
	BEFORE = "before"
	DURING = "during"
	AFTER = "after"
