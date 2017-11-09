import asyncio
import logging
import json
import os
import uuid
import shutil

import qzig

LOGGER = logging.getLogger(__name__)


class Model():
    def __init__(self, parent, load=None):
        self._parent = parent
        self._children = []
        self.attr = {}
        self.data = {}

        if load is None:
            self._init()
        else:
            self._load(load)

    @property
    def path(self):
        try:
            path = self._parent.path + self.name + "/" + self.id + "/"
        except AttributeError:
            path = self._rootdir + "store/"
        return path

    @property
    def child_path(self):
        return self.path + self.child_name

    @property
    def id(self):
        if self.data is not None:
            return self.data[":id"]

    @property
    def uuid(self):
        return str(uuid.uuid4())

    @property
    def name(self):
        return str(type(self).__name__).lower()

    @property
    def child_name(self):
        if not hasattr(self, "_child_name"):
            self._child_name = ""
            try:
                self._child_name = str(self.create_child().name).lower()
            except AttributeError:
                pass

        return self._child_name

    def __str__(self):  # pragma: no cover
        return "<%s attr: %s>" % (self.name, self.attr)

    def save(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        with open(self.path + self.name + ".json", 'w') as f:
            json.dump(
                {
                    "data": self.get_raw_data(),
                    "attr": self.attr
                },
                f,
                cls=qzig.util.QZigEncoder
            )

        if hasattr(self, "_children"):
            for c in self._children:
                c.save()

    def _parse(self):  # pragma: no cover
        pass

    def _load(self, load):
        self.data = load["data"]
        self.attr = load["attr"]
        self._parse()

    def load_children(self):
        for (root, dirs, files) in os.walk(self.child_path):
            dirs = [os.path.join(root, d) for d in dirs]

            child_name = self.child_name
            for dir in dirs:
                if not os.path.exists(dir + "/" + child_name + ".json"):
                    continue

                with open(dir + "/" + child_name + ".json", 'r') as f:
                    load = json.load(f)
                    c = self.create_child(load=load)
                    if isinstance(c, list):
                        for ch in c:
                            self._children.append(ch)
                            ch.load_children()
                    else:
                        self._children.append(c)
                        c.load_children()
        self._children_loaded()

    def _children_loaded(self):
        pass

    def send_put(self, url, data):
        url = "/" + self.name + "/" + self.id + url
        self._parent.send_put(url, data)

    def send_post(self, url, data):
        if url == "":
            url = "/" + self.name
        else:
            url = "/" + self.name + "/" + self.id + url
        self._parent.send_post(url, data)

    def send_delete(self, url=""):
        url = "/" + self.name + "/" + self.id + url
        self._parent.send_delete(url)

    def find_child(self, id):
        for c in self._children:
            if c.id == id:
                return c

        for c in self._children:
            res = c.find_child(id)
            if res is not None:
                return res

        return None

    def _remove_files(self):
        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:  # pragma: nocover
            pass

    @asyncio.coroutine
    def bind(self, endpoint_id, cluster_id):
        yield from self._parent.bind(endpoint_id, cluster_id)

    @asyncio.coroutine
    def permit(self, timeout):
        v = yield from self._parent.permit(timeout)
        return v

    @asyncio.coroutine
    def permit_with_key(self, node, code, timeout):
        v = yield from self._parent.permit_with_key(node, code, timeout)
        return v
