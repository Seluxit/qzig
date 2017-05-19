import logging
import json
import os

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
        return self.data[":id"]

    @property
    def name(self):
        return str(type(self).__name__).lower()

    @property
    def child_name(self):
        try:
            return str(self._child_class.__name__).lower()
        except:
            return ""

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

    def _parse(self):
        pass

    def _load(self, load):
        self.data = load["data"]
        self.attr = load["attr"]
        self._parse()

    def load_children(self):
        for (root, dirs, files) in os.walk(self.child_path):
            dirs = [os.path.join(root, d) for d in dirs]

            for dir in dirs:
                if not os.path.exists(dir + "/" + self.child_name + ".json"):
                    continue

                with open(dir + "/" + self.child_name + ".json", 'r') as f:
                    load = json.load(f)
                    c = self._child_class(self, load=load)
                    self._children.append(c)
                    c.load_children()
