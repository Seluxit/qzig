import asyncio
import logging
import uuid
import enum
import datetime

import qzig.model as model
import bellows.zigbee.zcl.clusters.general as general_clusters

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
        self._children = []

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

    @property
    def cluster_id(self):
        return self._parent.cluster_id

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

    @asyncio.coroutine
    def _delayed_report(self, time, value):
        s = self._parent.get_state(StateType.REPORT)
        if s is not None:
            yield from asyncio.sleep(time)
            s.attribute_updated(0, value)

    @asyncio.coroutine
    def change_state(self, data):
        if self.type == StateType.REPORT:
            return "Report state can't be changed"

        if self.cluster_id == general_clusters.OnOff.cluster_id:
            if data["data"] == "1":
                v = yield from self._parent._cluster.on()
            else:
                v = yield from self._parent._cluster.off()

            print(v)
            self.save()
            return True
        elif self.cluster_id == general_clusters.Identify.cluster_id:
            v = yield from self._parent._cluster.identify(int(data["data"]))
            print(v)
            return True
        elif self.cluster_id == -1:
            t = int(data["data"])
            v = yield from self._parent._parent._parent._parent._zb.app.permit(t)
            print(v)

            async_fun = getattr(asyncio, "ensure_future", asyncio.async)
            async_fun(self._delayed_report(t + 1, 0))

            return True
