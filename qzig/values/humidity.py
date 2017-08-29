import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Humidity(value.Value):
    _attribute = 0
    _bind = True

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Humidity",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Humidity",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 100
        self.data["number"].step = 0.01
        self.data["number"].unit = "percentage"

    def handle_report(self, attribute, data):
        if attribute == self._attribute:
            return (data / 100)
