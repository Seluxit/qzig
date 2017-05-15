import asyncio
import logging
import uuid
import json
import os

import device as device

LOGGER = logging.getLogger(__name__)


class Network():

    def __init__(self, id=None):
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:network-1.1",
            ":id": id,
            "name": "ZigBee Network",
            "device": []
        }
        self._devices = []

    @asyncio.coroutine
    def add_device(self, dev):
        d = self.get_device(str(dev.ieee))
        if d is None:
            d = device.Device()
            self._devices.append(d)

        yield from d.parse_device(dev)
        d.save()

    def load(self):
        try:
            with open("store/network.json", 'r') as f:
                raw = json.load(f)
                self.data = raw["data"]
        except:
            LOGGER.error("Failed to load network data")

    def save(self):
        if not os.path.exists("store"):
            os.makedirs("store")
        with open("store/network.json", 'w') as f:
            json.dump({"data": self.get_raw_data()}, f)

        for d in self._devices:
            d.save()

    def load_devices(self):
        for (root, dirs, files) in os.walk("store/devices/"):
            dirs = [os.path.join(root, d) for d in dirs]

            for dir in dirs:
                if not os.path.exists(dir + "/device.json"):
                    continue

                with open(dir + "/device.json", 'r') as f:
                    load = json.load(f)
                    d = device.Device(load=load)
                    self._devices.append(d)
                    d.load_values()

    def get_device(self, ieee):
        try:
            dev = next(d for d in self._devices if d.ieee == ieee)
        except StopIteration:
            dev = None
        return dev

    def get_raw_data(self):
        tmp = self.data
        tmp["device"] = []
        return tmp

    def get_data(self):
        tmp = self.get_raw_data()
        for d in self._devices:
            tmp["device"].append(d.get_data())

        return tmp

    @asyncio.coroutine
    def change_state(self, id, data):
        for dev in self._devices:
            res = yield from dev.change_state(id, data)
            if res is not None:
                return res

        return None
