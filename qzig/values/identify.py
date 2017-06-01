import asyncio
import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Identify(value.Value):
    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Identify",
            "permission": value.ValuePermission.WRITE_ONLY,
            "type": "Identify",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 120
        self.data["number"].step = 1
        self.data["number"].unit = "seconds"

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.identify(int(data))
        LOGGER.debug(v)
        self.save()
        return True
