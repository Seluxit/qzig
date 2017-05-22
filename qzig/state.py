import logging
import uuid
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

    def __init__(self, parent, state_type=None, id=None, load=None):
        self._parent = parent
        self.attr = {}

        if load is None:
            self._init(id, state_type)
        else:
            self._load(load)

    def _init(self, id, state_type):
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:state-1.1",
            ":id": id,
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

    def attribute_updated(self, attribute, data):
        LOGGER.debug("%d => %d" % (attribute, data))
        if attribute != 0:
            LOGGER.debug("We only handle attribute 0 for now")
            return

        self.data["timestamp"] = self.get_timestamp()
        self.data["data"] = str(data)

        self.save()

        self.send("", self.get_data())

    def zdo_command(self, *args):
        LOGGER.debug(args)
