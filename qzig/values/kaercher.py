import logging

import qzig.value as value
import qzig.status as status
import bellows.types as t
from bellows.zigbee.zcl import Cluster

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

    def handle_report(self, attribute, data):
        if attribute == self._attribute:
            return data
        elif attribute == 0x001:
            if data == 0:
                message = "OTA is not being requested"
            else:
                message = "OTA is requested every 24 hours"
            self._parent.add_status(status.StatusType.APPLICATION, status.StatusLevel.WARNING, message)
        elif attribute == 0x0100:
            if data == 1:
                self._parent.add_status(status.StatusType.APPLICATION, status.StatusLevel.ERROR, "Valve is blocked")
            elif data == 2:
                self._parent.add_status(status.StatusType.APPLICATION, status.StatusLevel.ERROR, "Valve not connected")


class FallbackEnable(value.Value):
    _attribute = 0
    _index = 0

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


class FallbackOnline(value.Value):
    _attribute = 1
    _index = 1

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


class FallbackStartTime(value.Value):
    _attribute = 2
    _index = 2

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


class FallbackDuration(value.Value):
    _attribute = 3
    _index = 3

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


class FallbackInterval(value.Value):
    _attribute = 4
    _index = 4

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
