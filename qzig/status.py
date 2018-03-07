import logging
import enum

import qzig.model as model

LOGGER = logging.getLogger(__name__)


class StatusLevel(enum.Enum):
    """Enum for Status Level"""
    IMPORTANT = "important"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class StatusType(enum.Enum):
    """Enum for the Status Types"""
    SYSTEM = "system"
    APPLICATION = "application"
    GATEWAY = "gateway"


class Status(model.Model):

    def __init__(self, parent, status_type=None, status_level=None, message=None):
        """Creates a new Status

        :param parent: The parent of the status
        :param status_type: The type of the status
        :param status_level: The level of the status
        :param message: The message of the status

        """
        self._parent = parent
        self.attr = {}
        self._children = []

        self._init(status_type, status_level, message)

    def _init(self, status_type, status_level, message):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:status-1.1",
            ":id": self._uuid,
            "type": status_type,
            "level": status_level,
            "timestamp": self._get_timestamp(),
            "message": message
        }

    def get_data(self):
        """Gets the status data

        :returns: The data of the status
        :rtype: Dict

        """
        return self.data
