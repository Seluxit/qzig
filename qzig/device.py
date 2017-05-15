import asyncio
import logging
import uuid
import os
import json

import model
import value

LOGGER = logging.getLogger(__name__)


class Device(model.Model):

    def __init__(self, id=None, load=None):
        self._values = []
        if load is None:
            self._init(id)
        else:
            self._parse(load)

    def _init(self, id):
        self._init_device = True
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:device-1.1",
            ":id": id,
            "name": "",
            "manufacturer": "",
            "product": "",
            "version": "",
            "serial": "",
            "description": "",
            "protocol": "ZigBee",
            "communication": "",
            "included": "1",
            "value": []
        }

    def _parse(self, load):
        self.data = load["data"]
        self.ieee = load["ieee"]
        self._init_device = False

    def save(self):
        if not os.path.exists("store/devices/" + self.data[":id"]):
            os.makedirs("store/devices/" + self.data[":id"])

        with open("store/devices/" + self.data[":id"] + "/device.json", 'w') as f:
            json.dump({
                "data": self.get_raw_data(),
                "ieee": str(self.ieee)
            }, f)

        for v in self._values:
            v.save()

    @asyncio.coroutine
    def parse_device(self, dev):
        self._dev = dev
        self.ieee = str(dev.ieee)
        if self._init_device:
            yield from self.read_device_info()

        for e_id in self._dev.endpoints:
            if e_id == 0:
                continue

            endpoint = self._dev.endpoints[e_id]
            for c_id in endpoint.clusters:
                cluster = endpoint.clusters[c_id]
                val = self.get_value(str(e_id), str(c_id))
                if val is None:
                    val = value.Value(self.data[":id"])
                    self._values.append(val)

                val.parse_cluster(endpoint, cluster)

    def get_value(self, endpoint, cluster):
        try:
            value = next(v for v in self._values
                         if v.endpoint_id == endpoint and v.cluster_id == cluster)
        except StopIteration:
            value = None
        return value

    def load_values(self):
        for (root, dirs, files) in os.walk("store/devices/" + self.data[":id"] + "/values/"):
            dirs = [os.path.join(root, d) for d in dirs]

            for dir in dirs:
                if not os.path.exists(dir + "/value.json"):
                    continue

                with open(dir + "/value.json", 'r') as f:
                    try:
                        load = json.load(f)
                    except:
                        LOGGER.debug("Failed to load %s", dir + "/value.json")
                        continue

                    v = value.Value(self.data[":id"], load=load)
                    self._values.append(v)
                    v.load_states()

    @asyncio.coroutine
    def read_device_info(self):
        if 1 not in self._dev.endpoints:
            LOGGER.error("Device %d do not have endpoint 1",
                         str(self._dev.ieee))
            return
        endp = self._dev.endpoints[1]
        if 0 not in endp.clusters:
            LOGGER.error("Device %d do not have cluster 0 on endpoint 1",
                         str(self._dev.ieee))
            return
        cluster = endp.clusters[0]

        LOGGER.debug("Reading attributes")
        v = yield from cluster.read_attributes([0, 1, 2, 3, 4, 5])
        self._handle_attributes_reply(v)
        v = yield from cluster.read_attributes([10])
        self._handle_attributes_reply(v)

    def _handle_attributes_reply(self, attr):
        if attr[1]:
            LOGGER.error("Failed to get attributes from device")
        else:
            self._parse_attributes(attr[0])

    def _parse_attributes(self, attr):
        version = []
        for t in attr:
            if t <= 3:
                version.append(attr[t])
            elif t == 4:
                self.data["manufacturer"] = attr[t].decode()
            elif t == 5:
                self.data["product"] = attr[t].decode()
                self.data["name"] = self.data["product"]
            elif t == 10:
                self.data["serial"] = attr[t].decode()

        if len(version):
            self.data["version"] = '.'.join(map(str, version))

    def get_raw_data(self):
        tmp = self.data
        tmp["value"] = []
        return tmp

    def get_data(self):
        tmp = self.get_raw_data()
        for v in self._values:
            d = v.get_data()
            if d is not None:
                tmp["value"].append(d)

        return tmp

    @asyncio.coroutine
    def change_state(self, id, data):
        for val in self._values:
            res = yield from val.change_state(id, data)
            if res is not None:
                return res

        return None
