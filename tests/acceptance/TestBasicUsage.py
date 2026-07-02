import datetime
import logging
import re
from enum import Enum
from typing import Any

from simputils.events.components.BasicEventCall import BasicEventCall
from simputils.events.mixins.EventfulMixin import EventfulMixin


class _MyEvents(str, Enum):
    INIT = "evt-init"
    BEFORE = "evt-before"
    AFTER = "evt-after"
    DESTRUCT = "evt-destruct"


class _MyObj(EventfulMixin):

    name: str | None = None
    init_ts: datetime.datetime = None
    process_start_ts: datetime.datetime = None
    process_end_ts: datetime.datetime = None
    destruct_ts: datetime.datetime = None
    triggered_event: list = None

    def __init__(self, name: str = None):
        super().__init__()
        self.triggered_event = []
        self.name = name

    def init(self, data: Any):
        self.init_ts = datetime.datetime.now()
        self.trigger(_MyEvents.INIT, self.init_ts, data=data)

    def process(self, data: Any):
        self.process_start_ts = datetime.datetime.now()
        self.trigger(_MyEvents.BEFORE, self.process_start_ts, data=data)

        logging.info("... Processing performed ...")

        self.process_end_ts = datetime.datetime.now()
        self.trigger(_MyEvents.AFTER, self.process_end_ts, data=data)

    def __del__(self):
        self.destruct_ts = datetime.datetime.now()
        self.trigger(_MyEvents.DESTRUCT, self.destruct_ts)

def _on_event_log(event: BasicEventCall, ts: datetime.datetime, data: Any = None):
    # TODO  `event` must be referring to an object representing event
    #       with all the necessary references on target objects
    logging.info("event=%s; ts=%s; data=%s", event.event.name, ts, data)


def check_log_message(caplog, event: _MyEvents, data: Any = None, pattern: str = None):
    pattern = pattern or r".*event=%s; ts=[\d\s:.-]*; data=%s.*"
    for msg in caplog.messages:
        expected_pattern = pattern % (event.value, data)
        sub = re.match(expected_pattern, msg)
        if sub is not None:
            return True
    return False
    # return any([re.match(pattern % (event.value, data), msg) is not None for msg in caplog.messages])


class TestBasicUsage:

    def test_basic_usage(self, caplog):
        obj = _MyObj(name="Panda")
        obj.on(_MyEvents.INIT, _on_event_log)
        obj.on(_MyEvents.DESTRUCT, _on_event_log)
        data = "init test"

        obj.init(data)
        assert check_log_message(caplog, _MyEvents.INIT, data)

        obj.process("processing test")

        del obj
        assert check_log_message(caplog, _MyEvents.DESTRUCT)

