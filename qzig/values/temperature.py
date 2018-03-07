import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Temperature(value.Value):
    """Class to handle Temperature measurements"""
    _bind = True
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Temperature",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Temperature",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = -273.15
        self.data["number"].max = 327.67
        self.data["number"].step = 0.01
        self.data["number"].unit = "celcius"

    def _handle_report(self, attribute, data):
        """Handles a temperature report and converts it

        Converts 1220 to 12.20

        :param attribute: The id of the attribute
        :param data: The reported temperature data
        :returns: The converted temperature data
        :rtype: Float

        """
        if attribute == self._attribute:
            return (data / 100)
