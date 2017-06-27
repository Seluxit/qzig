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
        self.save()

    def create_child(self, **args):
        return NetworkPermit(self, **args)


class NetworkPermit(value.Value):
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

    def handle_report(self, attribute, data):
        return data

    @asyncio.coroutine
    def handle_control(self, data):
        t = int(data)
        v = yield from self.permit(t)
        LOGGER.debug(v)

        self.delayed_report(0, t)
        self._report_fut = self.delayed_report(t, 0)

        return True
