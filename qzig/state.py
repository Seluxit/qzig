import asyncio
import logging
import enum

import qzig.model as model
from bellows.zigbee.exceptions import DeliveryError

LOGGER = logging.getLogger(__name__)


class StateType(enum.Enum):
    """Enum for State Type"""
    REPORT = "Report"
    CONTROL = "Control"


class StateStatus(enum.Enum):
    """Enum for State Status"""
    SEND = "Send"
    PENDING = "Pending"
    FAILED = "Failed"


class State(model.Model):

    def __init__(self, parent, state_type=None, load=None):
        """Creates a new State

        :param parent: The parent of the state
        :param state_type: The state type
        :param load: Data it should load

        """
        self._parent = parent
        self.attr = {}
        self._children = []

        if load is None:
            self._init(state_type)
        else:
            self._load(load)

    def _init(self, state_type):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:state-1.1",
            ":id": self._uuid,
            "type": state_type,
            "status": StateStatus.SEND,
            "timestamp": self._get_timestamp(),
            "data": "0"
        }

        if self._parent.data.get("number") is None:
            self.data["data"] = ""

    def _parse(self):
        self.data["type"] = StateType(self.data["type"])

    @property
    def type(self):
        """Returns the type of the state

        :returns: The type of the state
        :rtype: String

        """
        return self.data["type"]

    def _get_raw_data(self):
        tmp = self.data
        return tmp

    def zdo_command(self, *args):
        """zdo command stub"""
        pass

    def attribute_updated(self, attribute, data):
        """Called when an attribute is updated

        :param attribute: The id of the attribute
        :param data: The new attribute data

        """
        data = self._parent._handle_report(attribute, data)
        if data is None:
            return

        LOGGER.debug("Attribute %s change to %s on %s", attribute, data, self._parent.data["name"])

        self.data["timestamp"] = self._get_timestamp()
        self.data["data"] = str(data)

        self._save()

        self._send_put("", self.get_data())

    def cluster_command(self, aps_frame, tsn, command_id, args):
        """Cluster Command handler stub"""
        pass  # pragma: nocover

    @asyncio.coroutine
    def change_state(self, data):
        """Handle a request to change state

        :param data: The new state
        :returns: The result of the state change
        :rtype: String

        """
        if self.type == StateType.REPORT:
            return "Report state can't be changed"

        self.data["data"] = str(data["data"])

        try:
            res = yield from self._parent._handle_control(data["data"])
            return res
        except DeliveryError as e:
            LOGGER.error("Faild to send message")
            return str(e)
        except Exception as e:
            LOGGER.error("Exception: %s (%s)", e, type(e))
            print(traceback.print_exc())
            return str(e)
