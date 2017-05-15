import asyncio
import logging

import zigbee as zigbee
import json_rpc as json_rpc
import network as network

LOGGER = logging.getLogger(__name__)


class Application():

    def __init__(self, device, database):
        self._dev = device
        self._database = database
        self._devices = {}
        self._network = network.Network("9e32e295-60be-4b9c-91d9-cd7942756496")

    @asyncio.coroutine
    def init(self):
        yield from self.connect()
        yield from self._load()
        self._send_full_network()

    @asyncio.coroutine
    def connect(self):
        self._zb = zigbee.ZigBee(self, self._dev, self._database)
        yield from self._zb.connect()

        self._rpc = yield from json_rpc.connect(self)

    def _load(self):
        self._network.load()
        self._network.load_devices()
        for ieee, dev in self._zb.devices():
            yield from self._network.add_device(dev)

    def _send_full_network(self):
        self._rpc.post("/network", self._network.get_data())
        self._network.save()

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
        return True

    def POST(self, url, data):
        LOGGER.debug(url)
        LOGGER.debug(data)
        return True

    def GET(self, url):
        LOGGER.debug(url)
        return True

    def DELETE(self, url):
        LOGGER.debug(url)
        return True
