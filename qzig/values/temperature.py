import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Temperature(value.Value):
    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Temperature",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Temperature",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = -100
        self.data["number"].max = 100
        self.data["number"].step = 0.1
        self.data["number"].unit = "celcius"

    def handle_report(self, attribute, data):
        if attribute == 0:
            return data
