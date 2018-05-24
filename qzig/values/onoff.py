import asyncio
import logging

import qzig.value as value
import bellows.types as t

LOGGER = logging.getLogger(__name__)


class OnOff(value.Value):
    """Value to handle the On/Off command"""
    _bind = True
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
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
        if self._get_manufacturer() == "Kaercher":
            self.data["number"].unit = "states"
            self._manufacturer = 0x122C
        else:
            self.data["number"].unit = "boolean"

    @asyncio.coroutine
    def _handle_control(self, data):
        if data == "1":
            v = yield from self._cluster.on()
        else:
            v = yield from self._cluster.off()

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class OnTime(value.Value):
    """Value to handle the on-time command"""
    _bind = False
    _attribute = 0x4001

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "On Time",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Time",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 6553
        self.data["number"].step = 1
        if self._get_manufacturer() == "Kaercher":
            self.data["number"].unit = "minutes"
            self._manufacturer = 0x122C
        else:
            self.data["number"].unit = "seconds"

    @asyncio.coroutine
    def _handle_control(self, data):
        raw_data = int(data) * 10
        v = yield from self._cluster.write_attributes({self._attribute: raw_data})

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class OnTimeout(value.Value):
    """value to handle the on timeout command"""
    _bind = False
    _attribute = 0x42

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "On With Timeout",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "On/Off",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 6553
        self.data["number"].step = 1
        if self._get_manufacturer() == "Kaercher":
            self.data["number"].unit = "minutes"
            self._manufacturer = 0x122C
        else:
            self.data["number"].unit = "seconds"

    @asyncio.coroutine
    def _handle_control(self, data=None):
        if self._get_manufacturer() == "Kaercher":
            data = int(data)
            v = yield from self._cluster.request(False, 0x42, (t.uint16_t, ), data, manufacturer=0x122C)
        else:
            v = yield from self._cluster.on_with_timed_off()

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class BlockageCounter(value.Value):
    """Value to show the blockage counter"""
    _bind = False
    _attribute = 1
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Blockage Counter",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Counter",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 0xFFFF
        self.data["number"].step = 1
        self.data["number"].unit = ""
