import asyncio
import logging
import sys

import qzig.model as model
import qzig.value as value
import qzig.values as values

LOGGER = logging.getLogger(__name__)


class Device(model.Model):

    def __init__(self, parent, load=None):
        self._parent = parent
        self._children = []

        if load is None:
            self._init()
        else:
            self._load(load)

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:device-1.1",
            ":id": self.uuid,
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

    @property
    def name(self):
        return "device"

    @property
    def child_name(self):
        return "value"

    def create_child(self, **args):
        if "load" in args and "attr" in args["load"]:
            cid = args["load"]["attr"]["cluster_id"]
            c = values.get_value_class(cid)
        elif "cluster_id" in args:
            cid = args["cluster_id"]
            c = values.get_value_class(cid)

        if c is None:
            return value.Value(self, **args)
        else:
            return c(self, **args)

    @property
    def ieee(self):
        return self.attr["ieee"]

    @asyncio.coroutine
    def parse_device(self, dev):
        self._dev = dev
        self.attr["ieee"] = str(dev.ieee)
        if self.data["version"] == "":
            yield from self.read_device_info()

        for e_id in self._dev.endpoints:
            endpoint = self._dev.endpoints[e_id]
            if e_id == 0:
                continue

            for c_id in endpoint.clusters:
                cluster = endpoint.clusters[c_id]
                val = self.add_value(e_id, c_id)
                val.parse_cluster(endpoint, cluster)

    def add_value(self, endpoint_id, cluster_id):
        val = self.get_value(endpoint_id, cluster_id)
        if val is None:
            val = self.create_child(endpoint_id=endpoint_id, cluster_id=cluster_id)
            self._children.append(val)
        else:
            val._parent = self
        return val

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
            except:  # pragma: no cover
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
    def delete(self):
        v = yield from self._dev.zdo.leave()
        print(v)
        self._remove_files()

        return True
