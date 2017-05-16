import asyncio
import logging
import uuid
import enum
import os
import json
import datetime

import qzig.util

LOGGER = logging.getLogger(__name__)


class StateType(enum.Enum):
    REPORT = "Report"
    CONTROL = "Control"


class StateStatus(enum.Enum):
    SEND = "Send"
    PENDING = "Pending"
    FAILED = "Failed"


class State():

    def __init__(self, device_id, value_id, state_type=None, id=None, load=None):
        self.device_id = device_id
        self.value_id = value_id
        if load is None:
            self._init(id, state_type)
        else:
            self._parse(load)

    def _init(self, id, state_type):
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:state-1.1",
            ":id": id,
            "type": state_type,
            "status": StateStatus.SEND,
            "timestamp": self.get_timestamp(),
            "data": "0"
        }

    def get_timestamp(self):
        t = str(datetime.datetime.utcnow()).split('.')[0]
        return t.replace(" ", "T") + 'Z'

    def _parse(self, load):
        self.data = load["data"]
        self.device_id = load["device_id"]
        self.value_id = load["value_id"]

    def get_raw_data(self):
        tmp = self.data
        return tmp

    def get_data(self):
        tmp = self.get_raw_data()
        return tmp

    def save(self):
        if not os.path.exists("store/devices/" + self.device_id + "/values/" + self.value_id + "/states/"):
            os.makedirs("store/devices/" + self.device_id + "/values/" + self.value_id + "/states/")

        with open("store/devices/" + self.device_id + "/values/" + self.value_id + "/states/" + self.data[":id"] + ".json", 'w') as f:
            json.dump({
                "data": self.get_raw_data(),
                "device_id": self.device_id,
                "value_id": self.value_id,
            }, f, cls=qzig.util.QZigEncoder)
