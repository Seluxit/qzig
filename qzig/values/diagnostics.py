import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Diagnostics(value.Value):
    _bind = True
    _attribute = 0x011D

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "RSSI",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Rssi",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 255
        self.data["number"].step = 1
        self.data["number"].unit = ""
