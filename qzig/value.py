import asyncio
import logging
import uuid
import enum
import os
import json

import bellows.zigbee.zcl.clusters.general as zigbee_clusters

import qzig.state as state
import qzig.util


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
    max = 1
    encoding = ""


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


class Value():

    def __init__(self, device_id, id=None, load=None):
        self.device_id = device_id
        self._states = []
        if load is None:
            self._init(id)
        else:
            self._parse(load)

    def _init(self, id):
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": id,
            "name": "",
            "permission": ValuePermission.READ_ONLY,
            "type": "",
            "period": "",
            "delta": "",
            "number": ValueNumberType(),
            "status": ValueStatus.OK,
            "state": []
        }

    def _parse(self, load):
        self.data = load["data"]
        self.device_id = load["device_id"]
        self.endpoint_id = load["endpoint_id"]
        self.cluster_id = load["cluster_id"]

        self.data["permission"] = ValuePermission(self.data["permission"])
        self.data["status"] = ValueStatus(self.data["status"])

        if "number" in self.data:
            self.data["number"] = ValueNumberType(self.data["number"])
        elif "set" in self.data:
            self.data["set"] = ValueSetType(self.data["set"])
        elif "string" in self.data:
            self.data["string"] = ValueStringType(self.data["string"])
        elif "blob" in self.data:
            self.data["blob"] = ValueBlobType(self.data["blob"])
        elif "xml" in self.data:
            self.data["xml"] = ValueSetType(self.data["xml"])

    def parse_cluster(self, endpoint, cluster):
        self.endpoint_id = endpoint.endpoint_id
        self._endpoint = endpoint
        self.cluster_id = cluster.cluster_id
        self._cluster = cluster

        if self.cluster_id == zigbee_clusters.OnOff.cluster_id:
            self.data["name"] = "On/Off"
            self.data["permission"] = ValuePermission.READ_WRITE
            self.data["type"] = "On/Off"
            self.data["number"].min = 0
            self.data["number"].max = 1
            self.data["number"].step = 1
            self.data["number"].unit = "boolean"

            self.add_states([state.StateType.REPORT, state.StateType.CONTROL])
        elif self.cluster_id == zigbee_clusters.Identify.cluster_id:
            self.data["name"] = "Identify"
            self.data["permission"] = ValuePermission.WRITE_ONLY
            self.data["type"] = "Identify"
            self.data["number"].min = 0
            self.data["number"].max = 120
            self.data["number"].step = 1
            self.data["number"].unit = "seconds"

            self.add_states([state.StateType.CONTROL])
        else:
            self.data = None

        if self.data is not None:
            cluster.add_listener(self)

    def cluster_command(self, aps_frame, tsn, command_id, args):
        LOGGER.debug("APS: %d TSN: %d CMD: %d ARGS %s", aps_frame, tsn, command_id, args)

    def add_states(self, types):
        for t in types:
            s = self.get_state(t.value)
            if s is None:
                s = state.State(self.device_id, self.data[":id"], t)
                self._states.append(s)

    def get_state(self, state_type):
        try:
            state = next(s for s in self._states
                         if s.data["type"] == state_type)
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
        if len(self._states):
            self.data["state"] = []
        for s in self._states:
            tmp["state"].append(s.get_data())
        return tmp

    def save(self):
        if self.data is None:
            return

        if not os.path.exists("store/devices/" + self.device_id + "/values/" + self.data[":id"]):
            os.makedirs("store/devices/" + self.device_id + "/values/" + self.data[":id"])

        with open("store/devices/" + self.device_id + "/values/" + self.data[":id"] + "/value.json", 'w') as f:
            json.dump({
                "data": self.get_raw_data(),
                "device_id": self.device_id,
                "endpoint_id": str(self.endpoint_id),
                "cluster_id": str(self.cluster_id)
            }, f, cls=qzig.util.QZigEncoder)

        for s in self._states:
            s.save()

    def load_states(self):
        for (root, dirs, files) in os.walk("store/devices/" + self.device_id + "/values/" + self.data[":id"] + "/states/"):
            files = [os.path.join(root, f) for f in files]
            files = [f for f in files if f.endswith(".json")]

            for file in files:
                with open(file, 'r') as f:
                    try:
                        load = json.load(f)
                    except:
                        LOGGER.error("Failed to load %s", file)
                        continue

                    s = state.State(self.device_id, self.data[":id"], load=load)
                    self._states.append(s)

    @asyncio.coroutine
    def change_state(self, id, data):
        for s in self._states:
            if s.data[":id"] == id:
                if s.data["type"] == state.StateType.REPORT:
                    return "Report state can't be changed"

                if self.cluster_id == zigbee_clusters.OnOff.cluster_id:
                    if data["data"] == "1":
                        v = yield from self._cluster.on()
                    else:
                        v = yield from self._cluster.off()

                    print(v)
                    self.save()
                    return True
                elif self.cluster_id == zigbee_clusters.Identify.cluster_id:
                    v = yield from self._cluster.identify(int(data["data"]))
                    print(v)
                    return True
                else:
                    return False

        return None
