#!/bin/env python3
from datetime import datetime, timezone
from enum import Enum

from simputils.events.abstract.Eventful import Eventful
from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.components.BasicEventResult import BasicEventResult
from simputils.events.exceptions.InterruptEventSequence import InterruptEventSequence


class MyEventEnum(str, Enum):

	BEFORE = "evt-before"
	AFTER = "evt-after"


class MyObj(Eventful):

	@classmethod
	def _display_summary(cls, sub_results: list):
		for item in sub_results:
			for desc in item:
				print(">>> ", desc)

	def prepare_data(self, name: str, surname: str, age: int):
		sub_res = self.event_run(MyEventEnum.BEFORE, name, surname, age)
		if sub_res:
			self._display_summary(sub_res.results)
		else:
			print("No pre-processed description prepared")

		sub_res_2 = self.event_run(MyEventEnum.AFTER, datetime.now(timezone.utc))

		return self._preprocess_results(sub_res) + self._preprocess_results(sub_res_2)

	@classmethod
	def _preprocess_results(cls, sub_res: BasicEventResult) -> list:
		res = []
		call: BasicEventCall
		for call, call_res in sub_res:
			if call_res is not None:
				for item in call_res:
					res.append(item)
			if call.interrupted:
				res.append(f"{call.callback.__name__}() INTERRUPTED")
		return res


def on_before(call: BasicEventCall, name: str, surname: str, age: int) -> list[str]:
	res = [
		f"[[event \"{call.event}\" adjusted through `{call.callback.__name__}()` callback]]",
		f"Name: {name} {surname}",
		f"Age: {age}"
	]
	return res


def on_after(call: BasicEventCall, ts: datetime) -> list[str]:
	res = [
		f"[[event \"{call.event}\" adjusted through `{call.callback.__name__}()` callback]]",
		f"Finished at: {ts}"
	]
	raise InterruptEventSequence(res)
	return res


def main():
	obj = MyObj()
	obj.on_event(MyEventEnum.BEFORE, on_before)
	obj.on_event(MyEventEnum.AFTER, on_after)
	obj.on_event(MyEventEnum.AFTER, on_after)

	descriptions = obj.prepare_data("Ivan", "Ponomarev", 35)

	print(f"Resulting descriptions:")
	for desc in descriptions:
		print("##\t", desc)


if __name__ == "__main__":
	main()
