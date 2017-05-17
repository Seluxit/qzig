import asyncio
import logging
import uuid
import json
import os

import qzig.model as model
import qzig.device as device

LOGGER = logging.getLogger(__name__)


class Network(model.Model):

    def __init__(self, id=None):
        if id is None:
            id = str(uuid.uuid4())

        self.data = {
            ":type": "urn:seluxit:xml:bastard:network-1.1",
            ":id": id,
            "name": "ZigBee Network",
            "device": []
        }
        self.attr = {}
        self._children = []
        self._child_class = device.Device

    @asyncio.coroutine
    def add_device(self, dev):
        d = self.get_device(str(dev.ieee))
        if d is None:
            d = device.Device(self)
            self._children.append(d)
        else:
            d._parent = self

        yield from d.parse_device(dev)
        d.save()

    def load(self):
        try:
            with open("store/network.json", 'r') as f:
                raw = json.load(f)
                self.data = raw["data"]
                self.attr = raw["attr"]
        except:
            LOGGER.error("Failed to load network data")
        self.load_children()

    def get_device(self, ieee):
        try:
            print(ieee)
            print(self._children)
            dev = next(d for d in self._children if d.ieee == ieee)
        except StopIteration:
            dev = None
        return dev

    def get_raw_data(self):
        tmp = self.data
        tmp["device"] = []
        return tmp

    def get_data(self):
        tmp = self.get_raw_data()
        for d in self._children:
            tmp["device"].append(d.get_data())

        return tmp

    @asyncio.coroutine
    def change_state(self, id, data):
        for dev in self._children:
            res = yield from dev.change_state(id, data)
            if res is not None:
                return res

        return None
