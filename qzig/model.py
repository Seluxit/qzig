import asyncio
import logging
import json
import os
import uuid
import shutil
import datetime

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
    def _path(self):
        try:
            path = self._parent._path + self.name + "/" + self.id + "/"
        except AttributeError:
            path = self._rootdir + "store/"
        return path

    @property
    def _child_path(self):
        return self._path + self._get_child_name()

    @property
    def id(self):
        """Returns the id of the model

        :returns: The id of the model
        :rtype: String

        """
        if self.data is not None:
            return self.data[":id"]

    @property
    def _uuid(self):
        return str(uuid.uuid4())

    @property
    def name(self):
        """The name of the object

        :returns: The name of the object
        :rtype: String

        """
        if hasattr(self, "_name"):
            return self._name
        else:
            return str(type(self).__name__).lower()

    def _get_manufacturer(self):
        return self._parent._get_manufacturer()

    def _get_child_name(self):
        if not hasattr(self, "_child_name"):
            self._child_name = ""
            try:
                self._child_name = str(self._create_child().name).lower()
            except AttributeError:
                pass

        return self._child_name

    def __str__(self):  # pragma: no cover
        return "<%s attr: %s>" % (self.name, self.attr)

    def _save(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)

        with open(self._path + self.name + ".json", 'w') as f:
            json.dump(
                {
                    "data": self._get_raw_data(),
                    "attr": self.attr
                },
                f,
                cls=qzig.util.QZigEncoder
            )

        if hasattr(self, "_children"):
            for c in self._children:
                c._save()

    def _parse(self):  # pragma: no cover
        pass

    def _load(self, load):
        self.data = load["data"]
        self.attr = load["attr"]
        self._parse()

    def _load_children(self):
        for (root, dirs, files) in os.walk(self._child_path):
            dirs = [os.path.join(root, d) for d in dirs]

            child_name = self._get_child_name()
            for dir in dirs:
                if not os.path.exists(dir + "/" + child_name + ".json"):
                    continue

                with open(dir + "/" + child_name + ".json", 'r') as f:
                    try:
                        load = json.load(f)
                    except ValueError:
                        LOGGER.debug("Invalid JSON in " + dir + "/" + child_name + ".json")
                        continue

                    c = self._create_child(load=load)
                    if isinstance(c, list):
                        for ch in c:
                            self._children.append(ch)
                            ch._load_children()
                    else:
                        self._children.append(c)
                        c._load_children()
        self._children_loaded()

    def _children_loaded(self):
        pass

    def _send_put(self, url, data):
        url = "/" + self.name + "/" + self.id + url
        self._parent._send_put(url, data)

    def _send_post(self, url, data):
        if url == "":
            url = "/" + self.name
        else:
            url = "/" + self.name + "/" + self.id + url
        self._parent._send_post(url, data)

    def _send_delete(self, url=""):
        url = "/" + self.name + "/" + self.id + url
        self._parent._send_delete(url)

    def _find_child(self, id):
        for c in self._children:
            if c.id == id:
                return c

        for c in self._children:
            res = c._find_child(id)
            if res is not None:
                return res

        return None

    def _remove_files(self):
        try:
            shutil.rmtree(self._path)
        except FileNotFoundError:  # pragma: nocover
            pass

    @asyncio.coroutine
    def _do_bind(self, endpoint_id, cluster_id):
        yield from self._parent._do_bind(endpoint_id, cluster_id)

    @asyncio.coroutine
    def _permit(self, timeout):
        v = yield from self._parent._permit(timeout)
        return v

    @asyncio.coroutine
    def _permit_with_key(self, node, code, timeout):
        v = yield from self._parent._permit_with_key(node, code, timeout)
        return v

    @asyncio.coroutine
    def _delete_device(self, ieee):
        v = yield from self._parent._delete_device(ieee)
        return v

    def _get_timestamp(self):
        """Convert current time to timestamp

        :returns: Current time as timestamp
        :rtype: String

        """
        t = str(datetime.datetime.utcnow()).split('.')[0]
        return t.replace(" ", "T") + 'Z'

    @asyncio.coroutine
    def _handle_get(self):
        res = yield from self._parent._handle_get()
        return res

    def get_data(self):
        """Gets the data of the model

        :returns: The data
        :rtype: Dict

        """
        tmp = self._get_raw_data()
        return tmp
