import sys
import asyncio
import logging

import bellows.types as t
import bellows.zigbee.util as util
import bellows.zigbee.device as bellows_device
import qzig.zigbee as zigbee
import qzig.json_rpc as json_rpc
import qzig.network as network
import qzig.gateway as gateway

LOGGER = logging.getLogger(__name__)


class Application():

    def __init__(self, device, network_id, **options):
        """Inits the QZig appliction with the device it should connect to

        :param device: The serial device to connect the ZigBee to
        :param network_id: The network id to use

        """
        self._dev = device
        self._network_id = network_id
        self._network = network.Network(self, network_id)
        self._installcode = None

        self.ssl = options.get("ssl")
        self._baudrate = options.get("baudrate") or 115200

        self.host = options.get("host") or "localhost"
        self.port = options.get("port") or 42005
        self._database = options.get("database") or "qzig.db"
        self._gateway = options.get("gateway") or gateway.Gateway
        self._transport = options.get("transport") or json_rpc
        self._loop = options.get("loop") or asyncio.get_event_loop()

        rootdir = options.get("rootdir")
        if rootdir:
            self._database = rootdir + self._database
            self._network._rootdir = rootdir

    def run(self):  # pragma: no cover
        """Main event loop"""
        try:
            self._loop.run_until_complete(self.init())
            self._loop.run_forever()
        except KeyboardInterrupt as e:
            LOGGER.warning("Caught keyboard interrupt. Canceling tasks...")
            self.close()
            for task in asyncio.Task.all_tasks():
                task.cancel()

            self._loop.run_until_complete(asyncio.sleep(.1))
        finally:
            LOGGER.debug("Stopping loop")
            self._loop.close()

    @asyncio.coroutine
    def init(self):
        """Setup the application, by connection to ZigBee and load old data"""

        yield from self._connect()
        yield from self._load()
        self._send_full_network()
        yield from self._clean_server_devices()

    @asyncio.coroutine
    def _connect(self):
        self._zb = zigbee.ZigBee(self, self._dev, self._database)
        yield from self._zb.connect(self._baudrate)

        self._rpc = yield from self._transport.connect(self)

    def close(self):
        """Closes the connection to zigbee and server"""
        try:
            if hasattr(self, "_zb"):
                self._zb.close()
            if hasattr(self, "_rpc"):
                self._rpc.close()
        except Exception:  # pragma: no cover
            e = sys.exc_info()[0]
            LOGGER.exception(e)

    def _load(self):
        self._network._load()

        while True:
            try:
                yield from self._load_devices()
                break
            except RuntimeError as e:  # pragma: no cover
                # Handle the error that the list of devices changes while looping it.
                LOGGER.warning(e)

        remove = []
        for dev in self._network._children:
            found = False
            if dev.ieee != "gateway":
                for ie in self._zb.ieees():
                    if str(dev.ieee) == str(ie):
                        found = True
                        break
                if not found:
                    remove.append(dev)

        for dev in remove:
            self._network.remove_device(dev)

    def _load_devices(self):
        for ieee, dev in self._zb.devices():
            yield from self._network.add_device(dev)

    def _send_put(self, url, data):
        """Sends a RPC PUT request

        :param url: The URL for the rpc call
        :param data: The rpc content

        """
        self._rpc.put(url, data)

    def _send_post(self, url, data):
        """Sends a RPC POST request

        :param url: The URL for the rpc call
        :param data: The rpc content

        """
        self._rpc.post(url, data)

    def _send_delete(self, url):
        """Sends a RPC DELETE request

        :param url: The URL for the rpc call

        """
        self._rpc.delete(url)

    def _send_full_network(self):
        self._rpc.post("/network", self._network.get_data())
        self._network._save()

    @asyncio.coroutine
    def _permit(self, timeout):
        v = yield from self._zb.controller.permit(timeout)
        return v

    @asyncio.coroutine
    def _permit_with_key(self, node, code, timeout):
        if node is None:
            LOGGER.debug("Permit join, so that we can get the IEEE from the device")
            if util.convert_install_code(code) is None:
                raise Exception("Invalid install code")

            self._installcode = code
            self._permit_timeout = timeout
            v = yield from self._zb.controller.permit(timeout)
        else:
            v = yield from self._zb.controller.permit_with_key(node, code, timeout)
        return v

    @asyncio.coroutine
    def _clean_server_devices(self):
        devices = yield from self._rpc.get("/network/" + self._network.id + "/device")

        if devices.get("code") is not None:  # pragma: no cover
            LOGGER.error("Failed to get devices from server: %s" % devices.get("message"))
            return

        # Make sure that we do not loop the string as an array
        if isinstance(devices["id"], str):
            devices["id"] = [devices["id"]]  # pragma: nocover

        for id in devices["id"]:
            dev = self._network._get_device("", id)
            if dev is None:
                self._rpc.delete("/network/" + self._network.id + "/device/" + id)

    def _split_url(self, url):
        path = url.split("/")
        id = path[-1]
        service = path[-2]
        return service, id

    @asyncio.coroutine
    def _delete_device(self, ieee):
        if type(ieee) is str:
            ieee = t.EmberEUI64([t.uint8_t(p, base=16) for p in ieee.split(':')])
        v = yield from self._zb.controller.remove(ieee)
        return v

    # Callbacks
    def device_left(self, device):
        """Callback when a device left the ZigBee network

        :param device: The device that left

        """
        LOGGER.debug("Device left %s", str(device.ieee))
        async_fun = getattr(asyncio, "ensure_future", asyncio.async)
        async_fun(self._zb.controller.remove(device.ieee))

    def device_removed(self, device):
        """Callback when a device was removed

        :param device: The device that was removed

        """
        LOGGER.debug("Device removed %s", str(device.ieee))
        self._network.remove_device(device)

    def device_joined(self, device):
        """Callback when a device joined the ZigBee network

        :param device: The device that joined

        """
        if self._installcode is None:
            LOGGER.debug("Device joined %s", str(device.ieee))
            gw = self._network._get_device("gateway")
            val = gw.get_value(-1, -1)
            if hasattr(val, "_report_fut"):
                val._report_fut.cancel()  # pragma: no cover
            val.delayed_report(0, 0, 0)
        else:
            LOGGER.debug("Device tried to join, setting install code")

            zb_dev = self._zb.controller.get_device(device.ieee)
            if zb_dev is not None:
                LOGGER.debug("Cleaning up old device, so that we can include it")
                zb_dev.initializing = False
                zb_dev.status = bellows_device.Status.NEW
                dev = self._network._get_device(str(device.ieee))
                if dev:
                    dev._rebind()

            async_fun = getattr(asyncio, "ensure_future", asyncio.async)
            async_fun(self._zb.controller.permit_with_key(device.ieee, self._installcode, self._permit_timeout))
            self._installcode = None

    def device_initialized(self, device):
        """Callback when a device is full initialized

        :param device: The device that has been initialized

        """
        LOGGER.debug("Device initlized %s", str(device.ieee))
        async_fun = getattr(asyncio, "ensure_future", asyncio.async)
        async_fun(self._network.add_device(device, True))

    def attribute_updated(self, cluster, attrid, value):
        """Callback when an attribute has been updated

        :param cluster: The cluster of the attribute
        :param attrid: The id of the attribute
        :param value: The value of the attribute

        """
        LOGGER.debug("Attributes updated %d %d %d", cluster, attrid, value)

    # RPC calls
    @asyncio.coroutine
    def put(self, url, data):
        """PUT request handler

        Only PUT on state is supported

        :param url: The url the put was send on
        :param data: The data from the put request
        :returns: The result of the put request
        :rtype: String

        """
        service, id = self._split_url(url)

        if service == "state":
            s = self._network._find_child(id)
            if s is None:
                return "Failed to find id %s" % id

            if s.name != "state":
                return "ID is not a state"

            res = yield from s.change_state(data)
            return res
        else:
            return "Invalid service (%s) in url" % service

    @asyncio.coroutine
    def post(self, url, data):
        """POST request handler

        POST is not handled

        :param url: The url the post was send on
        :param data: The data of the post request
        :returns: Always False
        :rtype: Boolean

        """
        service, id = self._split_url(url)

        return False

    @asyncio.coroutine
    def get(self, url, data=None):
        """Get request handler

        Only GET on device and state is supported

        :param url: The url the post was send on
        :param data: None
        :returns: The data the GET requested
        :rtype: String

        """
        service, id = self._split_url(url)

        if service == "state" or service == "device":
            s = self._network._find_child(id)
            if s is None:
                return "Failed to find id %s" % id

            if s.name != "state" and s.name != "device":
                return "ID is not a device or state"

            res = yield from s._handle_get()
            return res
        else:
            return "Invalid service (%s) in url" % service

    @asyncio.coroutine
    def delete(self, url, data=None):
        """Handles a DELETE request

        Only delete on device is supported

        :param url: The url to the object that should be deleted
        :param data: None
        :returns: The result of the request
        :rtype: String

        """
        service, id = self._split_url(url)

        if service == "device":
            d = self._network._find_child(id)
            if d is None:
                return "Failed to find id %s" % id

            if d.name != "device":
                return "ID is not a device"

            res = yield from d.delete()
            return res
        else:
            return "Invalid service (%s) in url" % service
