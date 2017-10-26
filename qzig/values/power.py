import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class PowerConfiguration(value.Value):
    _bind = True
    _attribute = 0x20

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Battery Voltage",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Voltage",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 0xff
        self.data["number"].step = 1
        self.data["number"].unit = "mV"

    def handle_report(self, attribute, data):
        if attribute == self._attribute:
            return (data * 100)
