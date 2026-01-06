#!/bin/env python3
from abc import ABCMeta
from enum import Enum

from simputils.events.abstract.Eventful import Eventful


class MyEvents(str, Enum):

	EVENT_ONE_BEFORE = "evt-one-before"
	EVENT_ONE_AFTER = "evt-one-after"


class MyObj(Eventful):

	def my_func(self):
		self.event_run(MyEvents.EVENT_ONE_BEFORE)
		self.event_run(MyEvents.EVENT_ONE_BEFORE, "one", "two", arg2=100, arg3=200)
		print("MY FUNC HERE")
		self.event_run(MyEvents.EVENT_ONE_AFTER)
		self.event_run(MyEvents.EVENT_ONE_AFTER, "three", arg2=1000, arg3=2000)

def my_callback_before(event, *args, **kwargs):
	print(f"My CALLBACK before: {event} | ", args, kwargs)

def my_callback_after(event, *args, **kwargs):
	print(f"My CALLBACK after: {event} | ", args, kwargs)


obj = MyObj()

uid1 = obj.on_event(MyEvents.EVENT_ONE_BEFORE, my_callback_before)
obj.on_event(MyEvents.EVENT_ONE_BEFORE, my_callback_before, arg2="my-arg-2", arg3="my-arg-3")

uid2 = obj.on_event(MyEvents.EVENT_ONE_AFTER, my_callback_after)
obj.on_event(MyEvents.EVENT_ONE_AFTER, my_callback_after, arg1="my-arg-1", arg2="my-arg-2")

obj.my_func()
obj.event_del(uid1)
obj.event_del(uid2)

print("---------------------")

obj.my_func()

# obj.event_purge()
