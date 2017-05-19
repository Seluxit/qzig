import asyncio
import logging
import uuid
import sys

import qzig.model as model
import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Device(model.Model):

    def __init__(self, parent, id=None, load=None):
        self._parent = parent
        self._children = []
        self._child_class = value.Value

        if load is None:
            self._init(id)
        else:
            self._load(load)

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
        self.attr = {
            "ieee": ""
        }

    def _parse(self):
        self._init_device = False

    @property
    def ieee(self):
        return self.attr["ieee"]

    @asyncio.coroutine
    def parse_device(self, dev):
        self._dev = dev
        self.attr["ieee"] = str(dev.ieee)
        if self._init_device:
            yield from self.read_device_info()

        for e_id in self._dev.endpoints:
            if e_id == 0:
                continue

            endpoint = self._dev.endpoints[e_id]
            for c_id in endpoint.clusters:
                cluster = endpoint.clusters[c_id]
                val = self.get_value(e_id, c_id)
                if val is None:
                    val = self._child_class(self)
                    self._children.append(val)
                else:
                    val._parent = self

                val.parse_cluster(endpoint, cluster)

    def get_value(self, endpoint, cluster):
        try:
            value = next(v for v in self._children
                         if str(v.endpoint_id) == str(endpoint) and str(v.cluster_id) == str(cluster))
        except StopIteration:
            value = None
        return value

    @asyncio.coroutine
    def read_device_info(self):
        for e_id in self._dev.endpoints:
            if e_id is 0:
                continue

            endp = self._dev.endpoints[e_id]
            if 0 not in endp.clusters:
                LOGGER.error("Device %s do not have cluster 0 on endpoint 1",
                             str(self._dev.ieee))
                continue
            cluster = endp.clusters[0]

            LOGGER.debug("Reading attributes")
            try:
                v = yield from cluster.read_attributes([0, 1, 2, 3, 4, 5])
                self._handle_attributes_reply(v)
                v = yield from cluster.read_attributes([10])
                self._handle_attributes_reply(v)
            except: # pragma: no cover
                e = sys.exc_info()[0]
                LOGGER.exception(e)

            return

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
        for v in self._children:
            d = v.get_data()
            if d is not None:
                tmp["value"].append(d)

        return tmp

    @asyncio.coroutine
    def change_state(self, id, data):
        for val in self._children:
            res = yield from val.change_state(id, data)
            if res is not None:
                return res

        return None
