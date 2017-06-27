import sys
import asyncio
import logging

import qzig.zigbee as zigbee
import qzig.json_rpc as json_rpc
import qzig.network as network
import qzig.gateway as gateway

LOGGER = logging.getLogger(__name__)


class Application():

    def __init__(self, device, network_id):
        self._dev = device
        self._database = "qzig.db"
        self._network = network.Network(self, network_id)
        self.host = "localhost"
        self.port = 42005
        self.ssl = None
        self._gateway = gateway.Gateway

    def gateway(self, gateway):
        self._gateway = gateway

    def rootdir(self, rootdir):
        self._database = rootdir + "qzig.db"
        self._network._rootdir = rootdir

    def rpc_connection(self, host, port, ssl):
        self.host = host
        self.port = port
        self.ssl = ssl

    def run(self):  # pragma: no cover
        """Main event loop"""
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.init())
            loop.run_forever()
        except KeyboardInterrupt as e:
            LOGGER.warning("Caught keyboard interrupt. Canceling tasks...")
            self.close()
            for task in asyncio.Task.all_tasks():
                task.cancel()

            loop.run_until_complete(asyncio.sleep(.1))
        finally:
            LOGGER.debug("Stopping loop")
            loop.close()

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
            if hasattr(self, "_zb"):
                self._zb.close()
            if hasattr(self, "_rpc"):
                self._rpc.close()
        except:  # pragma: no cover
            e = sys.exc_info()[0]
            LOGGER.exception(e)

    def _load(self):
        self._network.load()

        for ieee, dev in self._zb.devices():
            yield from self._network.add_device(dev)

    def send_put(self, url, data):
        self._rpc.put(url, data)

    def send_post(self, url, data):
        self._rpc.post(url, data)

    def send_delete(self, url):
        self._rpc.delete(url)

    def _send_full_network(self):
        self._rpc.post("/network", self._network.get_data())
        self._network.save()

    @asyncio.coroutine
    def permit(self, timeout):
        v = yield from self._zb.controller.permit(timeout)
        return v

    @asyncio.coroutine
    def _clean_server_devices(self):
        devices = yield from self._rpc.get("/network/" + self._network.id + "/device")
        for id in devices["id"]:
            dev = self._network.get_device("", id)
            if dev is None:
                self._rpc.delete("/network/" + self._network.id + "/device/" + id)

    def _split_url(self, url):
        path = url.split("/")
        id = path[-1]
        service = path[-2]
        return service, id

    # Callbacks
    def device_left(self, device):
        LOGGER.debug("Device left %s", str(device.ieee))
        async_fun = getattr(asyncio, "ensure_future", asyncio.async)
        async_fun(self._network.remove_device(device))

    def device_joined(self, device):
        LOGGER.debug("Device joined %s", str(device.ieee))
        gw = self._network.get_device("gateway")
        val = gw.get_value(-1, -1)
        if hasattr(val, "_report_fut"):
            val._report_fut.cancel()  # pragma: no cover
        val.delayed_report(0, 0)

    def device_initialized(self, device):
        LOGGER.debug("Device initlized %s", str(device.ieee))
        async_fun = getattr(asyncio, "ensure_future", asyncio.async)
        async_fun(self._network.add_device(device, True))

    def attribute_updated(self, cluster, attrid, value):
        LOGGER.debug("Attributes updated %d %d %d", cluster, attrid, value)

    # RPC calls
    @asyncio.coroutine
    def PUT(self, url, data):
        LOGGER.debug(url)
        LOGGER.debug(data)

        service, id = self._split_url(url)

        if service == "state":
            s = self._network.find_child(id)
            if s is None:
                return "Failed to find id %s" % id

            if s.name != "state":
                return "ID is not a state"

            res = yield from s.change_state(data)
            return res
        else:
            return "Invalid service (%s) in url" % service

    @asyncio.coroutine
    def POST(self, url, data):
        LOGGER.debug(url)
        LOGGER.debug(data)

        service, id = self._split_url(url)

        return False

    @asyncio.coroutine
    def GET(self, url, data=None):
        LOGGER.debug(url)

        service, id = self._split_url(url)

        if service == "state":
            s = self._network.find_child(id)
            if s is None:
                return "Failed to find id %s" % id

            if s.name != "state":
                LOGGER.debug(s)
                return "ID is not a state"

            res = yield from s.handle_get()
            return res
        else:
            return "Invalid service (%s) in url" % service

    @asyncio.coroutine
    def DELETE(self, url, data=None):
        LOGGER.debug(url)

        service, id = self._split_url(url)

        if service == "device":
            d = self._network.find_child(id)
            if d is None:
                return "Failed to find id %s" % id

            if d.name != "device":
                return "ID is not a device"

            res = yield from d.delete()
            return res
        else:
            return "Invalid service (%s) in url" % service
