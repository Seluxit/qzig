import asyncio
import logging
import json
import os

import qzig.model as model
import qzig.device as device

LOGGER = logging.getLogger(__name__)


class Network(model.Model):

    def __init__(self, parent, id, rootdir=""):
        self._parent = parent
        self.data = {
            ":type": "urn:seluxit:xml:bastard:network-1.1",
            ":id": id,
            "name": "ZigBee Network",
            "device": []
        }
        self.attr = {}
        self._children = []
        self._rootdir = rootdir

    def create_child(self, **args):
        return device.Device(self, **args)

    @asyncio.coroutine
    def add_device(self, dev):
        d = self.get_device(str(dev.ieee))
        if d is None:
            d = self.create_child()
            self._children.append(d)
        else:
            d._parent = self

        yield from d.parse_device(dev)
        d.save()

    def add_gateway(self, gw_class):
        gw = self.get_device("gateway")
        if gw is None:
            new_gw = gw_class(self)
        else:
            data = {
                "data": gw.data,
                "attr": gw.attr
            }
            self._children.remove(gw)
            new_gw = gw_class(self, load=data)
            new_gw._children = gw._children

        self._children.append(new_gw)

    def load(self):
        try:
            if os.path.exists(self.path + "network.json"):
                with open(self.path + "network.json", 'r') as f:
                    raw = json.load(f)
                    self.data = raw["data"]
                    self.attr = raw["attr"]
        except:
            LOGGER.exception("Failed to load network data")

        self.load_children()

    def get_device(self, ieee, id=None):
        try:
            dev = next(d for d in self._children
                       if d.ieee == ieee or d.id == id)
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
