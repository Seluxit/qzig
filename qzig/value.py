import asyncio
import logging
import enum

import qzig.model as model
import qzig.state as state


LOGGER = logging.getLogger(__name__)


class ValuePermission(enum.Enum):
    READ_ONLY = "r"
    WRITE_ONLY = "w"
    READ_WRITE = "rw"


class ValueNumberType():
    def __init__(self, data=None):
        if data is None:
            self.min = 0
            self.max = 0
            self.step = 0
            self.unit = ""
        else:
            self.min = data["min"]
            self.max = data["max"]
            self.step = data["step"]
            self.unit = data["unit"]


class ValueSetType():
    elements = []


class ValueStringType():
    def __init__(self, data=None):
        if data is None:
            self.max = 1
            self.encoding = ""
        else:
            self.max = data["max"]
            self.encoding = data["encoding"]


class ValueBlobType():
    max = 1
    encoding = ""


class ValueXmlType():
    xsd = ""
    namespace = ""


class ValueStatus(enum.Enum):
    OK = "ok"
    UPDATE = "update"
    PENDING = "pending"


class Value(model.Model):

    def __init__(self, parent, endpoint_id=None, cluster_id=None, load=None):
        self._parent = parent
        self._children = []
        self.attr = {
            "endpoint_id": endpoint_id,
            "cluster_id": cluster_id
        }

        if load is None:
            self._bind = True
            self._init()
            if self.data is None:
                return
            if self.data["permission"] == ValuePermission.READ_ONLY:
                self.add_states([state.StateType.REPORT])
            elif self.data["permission"] == ValuePermission.WRITE_ONLY:
                self.add_states([state.StateType.CONTROL])
            else:
                self.add_states([state.StateType.REPORT, state.StateType.CONTROL])
        else:
            self._bind = False
            self._load(load)

    def _init(self):
        self.data = None

    @property
    def name(self):
        return "value"

    def create_child(self, **args):
        return state.State(self, **args)

    @property
    def endpoint_id(self):
        return self.attr["endpoint_id"]

    @property
    def cluster_id(self):
        return self.attr["cluster_id"]

    def _parse(self):
        self.data["permission"] = ValuePermission(self.data["permission"])
        self.data["status"] = ValueStatus(self.data["status"])

        if "number" in self.data:
            self.data["number"] = ValueNumberType(self.data["number"])
        elif "string" in self.data:
            self.data["string"] = ValueStringType(self.data["string"])
        # elif "set" in self.data:
        #    self.data["set"] = ValueSetType(self.data["set"])
        # elif "blob" in self.data:
        #     self.data["blob"] = ValueBlobType(self.data["blob"])
        # elif "xml" in self.data:
        #    self.data["xml"] = ValueSetType(self.data["xml"])

    @asyncio.coroutine
    def parse_cluster(self, endpoint, cluster):
        self._endpoint = endpoint
        self._cluster = cluster

        if self.data is not None:
            rep = self.get_state(state.StateType.REPORT)
            if rep is not None:
                cluster.add_listener(rep)
                if self._bind:
                    yield from self.bind(self.endpoint_id, self.cluster_id)

    def add_states(self, types):
        for t in types:
            s = state.State(self, t)
            self._children.append(s)

    def get_state(self, state_type):
        try:
            state = next(s for s in self._children
                         if s.type == state_type)
        except StopIteration:
            state = None
        return state

    def get_raw_data(self):
        tmp = self.data
        if tmp is not None:
            tmp.pop('state', None)
        return tmp

    def get_data(self):
        tmp = self.get_raw_data()
        if tmp is None:
            return tmp
        if len(self._children):
            tmp["state"] = []
        for s in self._children:
            tmp["state"].append(s.get_data())
        return tmp

    def handle_report(self, attribute, data):  # pragma: no cover
        pass

    def delayed_report(self, time, value):
        async_fun = getattr(asyncio, "ensure_future", asyncio.async)
        return async_fun(self._delayed_report(time, value))

    @asyncio.coroutine
    def _delayed_report(self, time, value):
        s = self.get_state(state.StateType.REPORT)
        if s is not None:
            yield from asyncio.sleep(time)
            s.attribute_updated(0, value)

    @asyncio.coroutine
    def handle_control(self, data):  # pragma: no cover
        LOGGER.error("Called unhandled handle_control")
        pass

    @asyncio.coroutine
    def handle_get(self):  # pragma: no cover
        return False
