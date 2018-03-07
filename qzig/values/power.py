import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class PowerConfiguration(value.Value):
    """Class to handle Power measurements"""
    _bind = True
    _attribute = 0x20

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
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

    def _handle_report(self, attribute, data):
        """Handles a power report and converts it

        Convertes 123 to 12300

        :param attribute: The id of the attribute
        :param data: The reported power data
        :returns: The converted power data
        :rtype: Interger

        """
        if attribute == self._attribute:
            return (data * 100)
