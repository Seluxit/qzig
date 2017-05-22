import sys
import asyncio
import logging

import qzig.zigbee as zigbee
import qzig.json_rpc as json_rpc
import qzig.network as network

LOGGER = logging.getLogger(__name__)


class Application():

    def __init__(self, device, network_id, database, rootdir=""):
        self._dev = device
        self._database = database
        self._network = network.Network(self, network_id, rootdir)
        self._devices = {}

    @asyncio.coroutine
    def init(self):
        yield from self.connect()
        yield from self._load()
        self._send_full_network()
        yield from self._clean_server_devices()

    @asyncio.coroutine
    def connect(self):
        self._zb = zigbee.ZigBee(self, self._dev, self._database)
        yield from self._zb.connect()

        self._rpc = yield from json_rpc.connect(self)

    def close(self):
        try:
            self._zb.close()
            self._rpc.close()
        except:  # pragma: no cover
            e = sys.exc_info()[0]
            LOGGER.exception(e)

    def _load(self):
        self._network.load()

        for ieee, dev in self._zb.devices():
            yield from self._network.add_device(dev)

    def send(self, url, data):
        self._rpc.put(url, data)

    def _send_full_network(self):
        self._rpc.post("/network", self._network.get_data())
        self._network.save()

    @asyncio.coroutine
    def _clean_server_devices(self):
        devices = yield from self._rpc.get("/network/" + self._network.id + "/device")
        for id in devices[":id"]:
            if id == self._network.id:
                continue  # pragma: no cover
            dev = self._network.get_device("", id)
            if dev is None:
                self._rpc.delete("/network/" + self._network.id + "/device/" + id)

    @asyncio.coroutine
    def PUT(self, url, data):
        LOGGER.debug(url)
        LOGGER.debug(data)

        path = url.split("/")
        id = path[-1]
        service = path[-2]

        if service == "state":
            res = yield from self._network.change_state(id, data)
            if res is None:
                return "Failed to find id %s" % id
            else:
                return res
        else:
            return "Invalid service (%s) in url" % service

    @asyncio.coroutine
    def POST(self, url, data):
        LOGGER.debug(url)
        LOGGER.debug(data)
        return False

    @asyncio.coroutine
    def GET(self, url):
        LOGGER.debug(url)
        return False

    @asyncio.coroutine
    def DELETE(self, url):
        LOGGER.debug(url)
        return False
