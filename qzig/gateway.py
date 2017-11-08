import asyncio
import logging

import qzig.device as device
import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Gateway(device.Device):
    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:device-1.1",
            ":id": self.uuid,
            "name": "Gateway",
            "manufacturer": "Seluxit",
            "product": "Gateway",
            "version": "1.0",
            "serial": "",
            "description": "Device to control the gateway",
            "protocol": "ZigBee",
            "communication": "Always Online",
            "included": "1",
            "value": []
        }
        self.attr = {
            "ieee": "gateway",
            "init": True
        }
        self.add_value(-1, -1)
        self.add_value(-2, -2)
        self.add_value(-3, -3)
        self.save()

    def _children_loaded(self):
        if len(self._children) != 3:
            self.add_value(-1, -1)
            self.add_value(-2, -2)
            self.add_value(-3, -3)
            self.save()

        print(self._children)

    def create_child(self, **args):
        id = -1
        if "load" in args:
            id = args["load"]["attr"]["cluster_id"]
        else:
            id = args["cluster_id"]

        if id == -3:
            return [NetworkInstallKey(self, **args)]
        elif id == -2:
            return [NetworkJoinKey(self, **args)]
        else:
            return [NetworkPermit(self, **args)]


class NetworkPermit(value.Value):
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Permit Join",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Network Management",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 250
        self.data["number"].step = 1
        self.data["number"].unit = "seconds"

    @asyncio.coroutine
    def handle_control(self, data):
        t = int(data)
        v = yield from self.permit(t)
        LOGGER.debug(v)

        self.delayed_report(0, 0, t)
        self._report_fut = self.delayed_report(t, 0, 0)

        return True


class NetworkJoinKey(value.Value):
    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Join Key",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Network Management",
            "string": value.ValueStringType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["string"].encoding = "hexbinary"
        self.data["string"].max = 26

    def handle_report(self, attribute, data):  # pragma: no cover
        # test code => 000b57fffe42661a11223344556677884AF7
        #              000b57fffe42a0b311223344556677884AF7
        #              000b57fffe8074f411223344556677884AF7

        return data

    @asyncio.coroutine
    def handle_control(self, data):
        try:
            data = bytearray.fromhex(data)
        except Exception as e:
            LOGGER.error(e)
            return "Invalid hex data"

        if len(data) < 18:
            return "Install code has to be minimal 18 charaters, not %d" % len(data)

        node = data[0:8]
        code = data[8:]

        v = yield from self.permit_with_key(node, code, 180)
        LOGGER.debug(v)

        return True


class NetworkInstallKey(value.Value):
    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Install Key",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Network Management",
            "string": value.ValueStringType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["string"].encoding = "hexbinary"
        self.data["string"].max = 18

    def handle_report(self, attribute, data):  # pragma: no cover
        return data

    @asyncio.coroutine
    def handle_control(self, data):
        try:
            data = bytearray.fromhex(data)
        except Exception as e:
            LOGGER.error(e)
            return "Invalid hex data"

        if len(data) < 10:
            return "Install code has to be minimal 10 charaters, not %d" % len(data)

        v = yield from self.permit_with_key(None, data, 180)
        LOGGER.debug(v)

        return True
