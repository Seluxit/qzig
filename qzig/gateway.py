import logging
import uuid

import qzig.device as device

LOGGER = logging.getLogger(__name__)


class Gateway(device.Device):
    def _init(self, id):
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:device-1.1",
            ":id": id,
            "name": "Gateway",
            "manufacturer": "Seluxit",
            "product": "Gateway",
            "version": "1.0",
            "serial": "",
            "description": "Gateway device to control the gateway",
            "protocol": "ZigBee",
            "communication": "Always Listning",
            "included": "1",
            "value": []
        }
        self.attr = {
            "ieee": "gateway",
            "init": True
        }
        self.save()

    @property
    def name(self):
        return "device"
