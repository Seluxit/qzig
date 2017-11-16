import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class DiagnosticsRetries(value.Value):
    _bind = True
    _attribute = 0x011B

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Mac Retries",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Count",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 0xFFFF
        self.data["number"].step = 1
        self.data["number"].unit = ""


class DiagnosticsRssi(value.Value):
    _attribute = 0x011D

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
    _attribute = 0x011C

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
