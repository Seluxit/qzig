import asyncio
import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class OnOff(value.Value):
    _bind = True
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "On/Off",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "On/Off",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 1
        self.data["number"].step = 1
        self.data["number"].unit = "boolean"

    @asyncio.coroutine
    def handle_control(self, data):
        if data == "1":
            v = yield from self._cluster.on()
        else:
            v = yield from self._cluster.off()

        LOGGER.debug(v)

        if v[1] == 0:
            self.delayed_report(0, 0, v[0])

        self.save()
        return True
