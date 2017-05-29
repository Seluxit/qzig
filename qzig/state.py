import asyncio
import logging
import enum
import datetime

import qzig.model as model

LOGGER = logging.getLogger(__name__)


class StateType(enum.Enum):
    REPORT = "Report"
    CONTROL = "Control"


class StateStatus(enum.Enum):
    SEND = "Send"
    PENDING = "Pending"
    FAILED = "Failed"


class State(model.Model):

    def __init__(self, parent, state_type=None, load=None):
        self._parent = parent
        self.attr = {}
        self._children = []

        if load is None:
            self._init(state_type)
        else:
            self._load(load)

    def _init(self, state_type):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:state-1.1",
            ":id": self.uuid,
            "type": state_type,
            "status": StateStatus.SEND,
            "timestamp": self.get_timestamp(),
            "data": "0"
        }

    def _parse(self):
        self.data["type"] = StateType(self.data["type"])

    @property
    def type(self):
        return self.data["type"]

    def get_timestamp(self):
        t = str(datetime.datetime.utcnow()).split('.')[0]
        return t.replace(" ", "T") + 'Z'

    def get_raw_data(self):
        tmp = self.data
        return tmp

    def get_data(self):
        tmp = self.get_raw_data()
        return tmp

    def zdo_command(self, *args):
        LOGGER.debug(args)

    def attribute_updated(self, attribute, data):
        LOGGER.debug("%d => %d" % (attribute, data))
        data = self._parent.handle_report(attribute, data)

        if data is None:
            return

        self.data["timestamp"] = self.get_timestamp()
        self.data["data"] = str(data)

        self.save()

        self.send("", self.get_data())

    @asyncio.coroutine
    def change_state(self, data):
        if self.type == StateType.REPORT:
            return "Report state can't be changed"

        res = yield from self._parent.handle_control(data["data"])

        return res
