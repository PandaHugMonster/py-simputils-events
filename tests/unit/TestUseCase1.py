from threading import Lock

from simputils.events.SimpleEvent import SimpleEvent
from simputils.events.base import on_event
from simputils.events.generic.BasicEventingObject import BasicEventingObject

generic_lock = Lock()
resulting_list = []


class MyUseCase1(BasicEventingObject):
	"""
	Event Chains (Priority Based)
	* Order Updated Event
		* 1. Update DB -> 2. Recalculate Statistics -> 3. Set triggers -> 4. Notify company -> 5. E-mail user
	* User Profile Updated Event
		* 1. Update DB -> 2. Recalculate Statistics
	* New Product Notification Event
		* 1. Update DB -> 4. Notify company -> 5. E-mail user
	"""

	EVENT_ORDER_UPDATED = "order-updated"
	EVENT_USER_PROFILE_UPDATED = "user-profile-updated"
	EVENT_NEW_PRODUCT_NOTIFICATION = "new-product-notification"

	def get_permitted_events(self):
		return [
			self.EVENT_ORDER_UPDATED,
			self.EVENT_USER_PROFILE_UPDATED,
			self.EVENT_NEW_PRODUCT_NOTIFICATION,
		]

	@on_event(EVENT_ORDER_UPDATED, priority=1)
	@on_event(EVENT_USER_PROFILE_UPDATED, priority=1)
	@on_event(EVENT_NEW_PRODUCT_NOTIFICATION, priority=1)
	def _update_db(self, event: SimpleEvent):
		return {
			"index": event.priority,
			"response": "1. Updating DB",
		}

	@on_event(EVENT_ORDER_UPDATED, priority=2)
	@on_event(EVENT_USER_PROFILE_UPDATED, priority=2)
	def _recalculate_statistics(self, event: SimpleEvent):
		return {
			"index": event.priority,
			"response": "2. Recalculating statistics",
		}

	@on_event(EVENT_ORDER_UPDATED, priority=3)
	def _set_triggers(self, event: SimpleEvent):
		return {
			"index": event.priority,
			"response": "3. Setting triggers",
		}

	@on_event(EVENT_ORDER_UPDATED, priority=4)
	@on_event(EVENT_NEW_PRODUCT_NOTIFICATION, priority=4)
	def _notify_company(self, event: SimpleEvent):
		return {
			"index": event.priority,
			"response": "Notifying company",
		}

	@on_event(EVENT_ORDER_UPDATED, priority=5)
	@on_event(EVENT_NEW_PRODUCT_NOTIFICATION, priority=5)
	def _email_user(self, event: SimpleEvent):
		return {
			"index": event.priority,
			"response": "E-mailing user",
		}


class TestUseCase1:

	def test_user_profile_updated(self):
		obj = MyUseCase1()

		res = obj.trigger(MyUseCase1.EVENT_USER_PROFILE_UPDATED)
		assert len(res.events) == 2

		event = list(res.events.values())[0]
		assert event.result["index"] == 1
		assert event.handler.__name__ == "_update_db"

		event = list(res.events.values())[1]
		assert event.result["index"] == 2
		assert event.handler.__name__ == "_recalculate_statistics"

	def test_order_updated(self):
		obj = MyUseCase1()

		res = obj.trigger(MyUseCase1.EVENT_ORDER_UPDATED)
		assert len(res.events) == 5

		event = list(res.events.values())[0]
		assert event.result["index"] == 1
		assert event.handler.__name__ == "_update_db"

		event = list(res.events.values())[1]
		assert event.result["index"] == 2
		assert event.handler.__name__ == "_recalculate_statistics"

		event = list(res.events.values())[2]
		assert event.result["index"] == 3
		assert event.handler.__name__ == "_set_triggers"

		event = list(res.events.values())[3]
		assert event.result["index"] == 4
		assert event.handler.__name__ == "_notify_company"

		event = list(res.events.values())[4]
		assert event.result["index"] == 5
		assert event.handler.__name__ == "_email_user"

	def test_new_product_notification(self):
		obj = MyUseCase1()

		res = obj.trigger(MyUseCase1.EVENT_NEW_PRODUCT_NOTIFICATION)
		assert len(res.events) == 3

		event = list(res.events.values())[0]
		assert event.result["index"] == 1
		assert event.handler.__name__ == "_update_db"

		event = list(res.events.values())[1]
		assert event.result["index"] == 4
		assert event.handler.__name__ == "_notify_company"

		event = list(res.events.values())[2]
		assert event.result["index"] == 5
		assert event.handler.__name__ == "_email_user"
