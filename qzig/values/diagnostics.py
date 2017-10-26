import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class DiagnosticsRssi(value.Value):
    _bind = True
    _attribute = 0x011D
    _index = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "RSSI",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "rssi",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = -128
        self.data["number"].max = 0
        self.data["number"].step = 1
        self.data["number"].unit = ""


class DiagnosticsLinkQuality(value.Value):
    _bind = True
    _attribute = 0x011C
    _index = 1

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Link Quality",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "lqi",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 255
        self.data["number"].step = 1
        self.data["number"].unit = ""
