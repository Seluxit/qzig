import logging
import json
import os
import uuid

import qzig

LOGGER = logging.getLogger(__name__)


class Model():
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
        try:
            return str(self.create_child().name).lower()
        except:
            return ""

    def __str__(self):  # pragma: no cover
        return "<%s attr: %s>" % (self.name, self.attr)

    def save(self):
        if self.data is None:
            return

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
                    self._children.append(c)
                    c.load_children()

    def send(self, url, data):
        if hasattr(self, "_parent"):
            url = "/" + self.name + "/" + self.id + url
            self._parent.send(url, data)

    def find_child(self, id):
        for c in self._children:
            if c.id == id:
                return c

        for c in self._children:
            res = c.find_child(id)
            if res is not None:
                return res

        return None
