import asyncio
import logging
import json
import os

import qzig.model as model
import qzig.device as device

LOGGER = logging.getLogger(__name__)


class Network(model.Model):

    def __init__(self, parent, id):
        self._parent = parent
        self.data = {
            ":type": "urn:seluxit:xml:bastard:network-1.1",
            ":id": id,
            "name": "ZigBee Network",
            "device": []
        }

        self.attr = {}
        self._children = []
        self._rootdir = ""

    def create_child(self, **args):
        if self._parent._gateway is not None:
            try:
                if args["load"]["attr"]["ieee"] == "gateway":
                    return self._parent._gateway(self, **args)
            except KeyError:
                pass

        return device.Device(self, **args)

    @asyncio.coroutine
    def add_device(self, dev, post=False):
        d = self.get_device(str(dev.ieee))
        if d is None:
            d = self.create_child()
            self._children.append(d)
        else:
            d._parent = self

        yield from d.parse_device(dev)

        if post:
            d.send_post("", d.get_data())
        return d

    def add_gateway(self):
        if self._parent._gateway is None:
            return

        gw = self.get_device("gateway")
        if gw is not None:
            return gw

        new_gw = self._parent._gateway(self)

        self._children.append(new_gw)
        return new_gw

    def remove_device(self, dev):
        d = self.get_device(str(dev.ieee))
        if d is None:  # pragma: no cover
            LOGGER.error("Failed to find device to remove")
            return

        for d in self._children:
            if str(d.ieee) == str(dev.ieee):
                try:
                    self._children.remove(d)
                except ValueError:  # pragma: nocover
                    LOGGER.error("Failed to remove device from children")
                break

        d._remove_files()
        d.send_delete()

    def load(self):
        try:
            if os.path.exists(self.path + "network.json"):
                with open(self.path + "network.json", 'r') as f:
                    raw = json.load(f)
                    self.data = raw["data"]
                    self.attr = raw["attr"]
        except ValueError:
            LOGGER.exception("Failed to load network data")

        self.load_children()

        self.add_gateway()

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
