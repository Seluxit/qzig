import asyncio
import logging
import enum

import qzig.model as model
import qzig.status as status
import qzig.value as value
import qzig.values as values

LOGGER = logging.getLogger(__name__)


class PowerSource(enum.Enum):
    UNKNOWN = 0x00
    SINGLE_PHASE_MAINS = 0x01
    THREE_PHASE_MAINS = 0x02
    BATTERY = 0x03
    DC_SOURCE = 0x04
    EMERGENCY_MAINS_CONSTANTLY_POWERED = 0x05
    EMERGENCY_MAINS_AND_TRANSFER_SWITCH = 0x06
    UNKNOWN_BATTERY_BACKED = 0x80
    SINGLE_PHASE_MAINS_BATTERY_BACKED = 0x81
    THREE_PHASE_MAINS_BATTERY_BACKED = 0x82
    BATTERY_BATTERY_BACKED = 0x83
    DC_SOURCE_BATTERY_BACKED = 0x84
    EMERGENCY_MAINS_CONSTANTLY_POWERED_BATTERY_BACKED = 0x85
    EMERGENCY_MAINS_AND_TRANSFER_SWITCH_BATTERY_BACKED = 0x86


class Device(model.Model):
    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:device-1.1",
            ":id": self.uuid,
            "name": "",
            "manufacturer": "",
            "product": "",
            "version": "N/A",
            "serial": "",
            "description": "",
            "protocol": "ZigBee",
            "communication": "",
            "included": "1",
            "status": [],
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
            cls = values.get_value_class(cid)
            if isinstance(cls, list) and len(cls) > 1:
                for c in cls:
                    if c._index == args["load"]["attr"]["index"]:
                        cls = c
                        break
        elif "cluster_id" in args:
            cid = args["cluster_id"]
            cls = values.get_value_class(cid)

        vals = []
        if cls is None:
            vals.append(value.Value(self, **args))
        else:
            if not isinstance(cls, list):
                cls = [cls]
            for c in cls:
                vals.append(c(self, **args))

        for val in vals:
            if "endpoint_id" in args and args["endpoint_id"] != 1:
                val.data["name"] = val.data["name"] + " " + str(args["endpoint_id"])

        return vals

    @property
    def ieee(self):
        return self.attr["ieee"]

    @asyncio.coroutine
    def parse_device(self, dev):
        self._dev = dev
        self.attr["ieee"] = str(dev.ieee)
        if self.data["version"] == "N/A":
            yield from self.read_device_info()

        for e_id in self._dev.endpoints:
            endpoint = self._dev.endpoints[e_id]
            if e_id == 0:
                continue

            for c_id in endpoint.in_clusters:
                cluster = endpoint.in_clusters[c_id]
                yield from self._handle_cluster(endpoint, e_id, c_id, cluster)

            for c_id in endpoint.out_clusters:
                cluster = endpoint.out_clusters[c_id]
                yield from self._handle_cluster(endpoint, e_id, c_id, cluster)

        dev.zdo.add_listener(self)

        self.save()

    @asyncio.coroutine
    def _handle_cluster(self, endpoint, e_id, c_id, cluster):
        val = self.add_value(e_id, c_id)
        for v in val:
            yield from v.parse_cluster(endpoint, cluster)
            try:
                LOGGER.debug("Adding value %s", v.data["name"])
            except Exception:
                LOGGER.debug("No value handler for %d", v.cluster_id)

    def add_value(self, endpoint_id, cluster_id):
        values = []
        real = self.create_child(endpoint_id=endpoint_id, cluster_id=cluster_id)
        for r in real:
            val = self.get_value(endpoint_id, cluster_id, r.index)
            if val is None:
                val = r
            val._parent = self
            values.append(val)
            self._children.append(val)

        return values

    def get_value(self, endpoint, cluster, index=0):
        try:
            val = next(v for v in self._children
                       if str(v.endpoint_id) == str(endpoint) and str(v.cluster_id) == str(cluster) and str(v.index) == str(index))
        except StopIteration:
            return None
        return val

    @asyncio.coroutine
    def read_device_info(self):
        for e_id in self._dev.endpoints:
            if e_id is 0:
                continue

            endp = self._dev.endpoints[e_id]
            if 0 not in endp.in_clusters:
                LOGGER.error("Device %s do not have cluster 0 on endpoint %s",
                             str(self._dev.ieee), e_id)
                continue
            cluster = endp.in_clusters[0]

            LOGGER.debug("Reading attributes from device %s", str(self._dev.ieee))
            for attr in [[0, 1, 2, 3, 4], [5, 7, 10]]:
                try:
                    v = yield from cluster.read_attributes(attr)
                except:  # pragma: no cover
                    LOGGER.error("Failed to read attributes from device %s", str(self._dev.ieee))
                    return
                self._handle_attributes_reply(v)

    def _handle_attributes_reply(self, attr):
        if attr[1]:
            LOGGER.error("Failed to get attributes (%s) from device %s", attr[1], str(self._dev.ieee))
        if attr[0]:
            LOGGER.debug("Got attributes (%s) from device %s", attr[0], str(self._dev.ieee))
            self._parse_attributes(attr[0])

    def _parse_attributes(self, attr):
        version = []
        for t in attr:
            if t <= 3:
                version.append(attr[t])
            elif t == 4:
                self.data["manufacturer"] = attr[t].decode()
            elif t == 5:
                self.data["serial"] = attr[t].decode()
                self.data["product"] = self.data["serial"]
            elif t == 7:
                self.data["communication"] = PowerSource(attr[7]).name
            elif t == 10:
                self.data["serial"] = attr[t].decode()

        if len(version):
            self.data["version"] = '.'.join(map(str, version))

    def update_name(self):
        self.data["name"] = self.data["manufacturer"]
        if(len(self.data["product"])):
            self.data["name"] += " Product " + self.data["product"]

    def add_status(self, type, level, message):
        stat = status.Status(self, type, level, message)
        self.data["status"].insert(0, stat)
        stat.send_post("", stat.get_data())

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

    def device_announce(self, dev):
        LOGGER.debug("Device came online")

    @asyncio.coroutine
    def delete(self):
        v = yield from self._dev.zdo.leave()
        LOGGER.debug(v)
        self._remove_files()

        return True

    @asyncio.coroutine
    def bind(self, endpoint_id, cluster_id):
        try:
            yield from self._dev.zdo.bind(endpoint_id, cluster_id)
        except Exception:  # pragma: no cover
            LOGGER.error("Failed to bind to device")
