import asyncio
import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class AlarmResetAll(value.Value):
    _bind = True

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Reset All Alarms",
            "permission": value.ValuePermission.WRITE_ONLY,
            "type": "On/Off",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 1
        self.data["number"].step = 1
        self.data["number"].unit = "boolean"

    def handle_command(self, aps_frame, tsn, command_id, args):
        if command_id == 0:
            LOGGER.info("Alarm Report: Code %s on cluster %s", args[0], args[1])

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.reset_all()

        LOGGER.debug(v)

        return True