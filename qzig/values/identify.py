import asyncio
import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Identify(value.Value):
    """Class to send the identify command"""

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
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
    def _handle_control(self, data):
        v = yield from self._cluster.identify(int(data))

        LOGGER.debug("%s: %r", self.data["name"], v)

        self._save()
        return True
