import logging
import enum
import datetime

import qzig.model as model

LOGGER = logging.getLogger(__name__)


class StatusLevel(enum.Enum):
    IMPORTANT = "important"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class StatusType(enum.Enum):
    SYSTEM = "system"
    APPLICATION = "application"
    GATEWAY = "gateway"


class Status(model.Model):

    def __init__(self, parent, status_type=None, status_level=None, message=None):
        self._parent = parent
        self.attr = {}
        self._children = []

        self._init(status_type, status_level, message)

    def _init(self, status_type, status_level, message):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:status-1.1",
            ":id": self.uuid,
            "type": status_type,
            "level": status_level,
            "timestamp": self.get_timestamp(),
            "message": message
        }

    def get_timestamp(self):
        t = str(datetime.datetime.utcnow()).split('.')[0]
        return t.replace(" ", "T") + 'Z'

    def get_data(self):
        return self.data
