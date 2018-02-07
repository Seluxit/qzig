import logging
import asyncio

import qzig.value as value
import zigpy.types as t
from zigpy.zcl import Cluster

LOGGER = logging.getLogger(__name__)


class KaercherFallback(Cluster):
    cluster_id = 0xFC00
    name = "Kärcher Fallback"
    ep_attribute = 'kaercher_fallback'
    attributes = {
        0x0000: ('enable_flag', t.Bool),
        0x0001: ('online_flag', t.Bool),
        0x0002: ('start_time', t.uint16_t),
        0x0003: ('duration', t.uint8_t),
        0x0004: ('interval', t.uint8_t),
    }
    server_commands = {}
    client_commands = {}


class KaercherDeviceState(Cluster):
    cluster_id = 0xFC01
    name = "Kärcher Device State"
    ep_attribute = 'kaercher_device_state'
    attributes = {
        0x0000: ('device_state', t.uint16_t),
        0x0001: ('ota_update_request', t.Bool),
        0x0002: ('valve_error', t.uint8_t),
    }
    server_commands = {}
    client_commands = {}


class DeviceState(value.Value):
    _bind = True
    _attribute = 0
    _singleton = True
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Device State",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Device Mode",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 8
        self.data["number"].step = 1
        self.data["number"].unit = "State"


class DeviceStateOtaUpdate(value.Value):
    _attribute = 1
    _singleton = True
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Device State OTA Update",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "On/off",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 1
        self.data["number"].step = 1
        self.data["number"].unit = "Boolean"


class DeviceStateValueError(value.Value):
    _attribute = 0x0100
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Device State Valve Error",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "State",
            "number": value.ValueStringType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 2
        self.data["number"].step = 1
        self.data["number"].unit = "State"


class FallbackEnable(value.Value):
    _attribute = 0
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Fallback Enable",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Fallback Enable",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 1
        self.data["number"].step = 1
        self.data["number"].unit = "Boolean"

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: False if(data == "0") else True}, manufacturer=self._manufacturer)

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class FallbackOnline(value.Value):
    _attribute = 1
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Fallback Online",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Fallback Online",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 1
        self.data["number"].step = 1
        self.data["number"].unit = "Boolean"

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: False if(data == "0") else True}, manufacturer=self._manufacturer)

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class FallbackStartTime(value.Value):
    _attribute = 2
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Fallback Start Time",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Time",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 0xFFFF
        self.data["number"].step = 1
        self.data["number"].unit = "minute"

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: data}, manufacturer=self._manufacturer)

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class FallbackDuration(value.Value):
    _attribute = 3
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Fallback Duration",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Duration",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 0x5A
        self.data["number"].step = 1
        self.data["number"].unit = "minute"

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: data}, manufacturer=self._manufacturer)

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class FallbackInterval(value.Value):
    _attribute = 4
    _manufacturer = 0x122C

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Fallback Interval",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Interval",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 7
        self.data["number"].step = 1
        self.data["number"].unit = "Day"

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: data}, manufacturer=self._manufacturer)

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True
