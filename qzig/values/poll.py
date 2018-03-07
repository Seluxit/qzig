import asyncio
import logging

import qzig.value as value
import qzig.state as state

LOGGER = logging.getLogger(__name__)


class PollControlCheckInInterval(value.Value):
    """Class to handle the Check in Interval for Poll Control"""
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Check-in Interval",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Interval",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 7208960
        self.data["number"].step = 1
        self.data["number"].unit = "quarter seconds"

    @asyncio.coroutine
    def _handle_control(self, data):
        """Handles a control request to check in interval

        :param data: The new check in interval
        :returns: True if the check in interval was changed
        :rtype: Boolean

        """
        v = yield from self._cluster.write_attributes({self._attribute: data})

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class PollControlLongPollInterval(value.Value):
    """Class to handle the Long Poll Interval for Poll Control"""
    _attribute = 1

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Long Poll Interval",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Interval",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 4
        self.data["number"].max = 7208960
        self.data["number"].step = 1
        self.data["number"].unit = "quarter seconds"

    @asyncio.coroutine
    def _handle_control(self, data):
        """Handles a control request to change long poll interval

        :param data: New Long Poll interval
        :type data: int
        :returns: Return True if the new interval was set
        :rtype: Boolean

        """
        v = yield from self._cluster.set_long_poll_interval(data)

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class PollControlShortPollInterval(value.Value):
    """Class to handle the Short Poll Interval for Poll Control"""
    _attribute = 2

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Short Poll Interval",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Interval",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 1
        self.data["number"].max = 0xFFFF
        self.data["number"].step = 1
        self.data["number"].unit = "quarter seconds"

    @asyncio.coroutine
    def _handle_control(self, data):
        """Handles a control request to change short poll interval

        :param data: The new short poll interval
        :returns: True if the short poll interval was changed
        :rtype: Boolean

        """
        v = yield from self._cluster.set_short_poll_interval(data)

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class PollControlFastPollTimeout(value.Value):
    """Class to handle the Fast Poll Timeout for Poll Control"""
    _attribute = 3

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Fast Poll Timeout",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Timeout",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 1
        self.data["number"].max = 0xFFFF
        self.data["number"].step = 1
        self.data["number"].unit = "quarter seconds"

    def _handle_command(self, aps_frame, tsn, command_id, args):
        """Handles an incomming command with check in content

        :param aps_frame: The silabs aps frame
        :param tsn:
        :param command_id: The id of the command
        :param args: Arguments for the command

        """
        if command_id == 0x00:
            con = self._get_state(state.StateType.CONTROL)
            if con.data["data"] == "0":
                self._cluster.checkin_response(0, 0)
            else:
                self._cluster.checkin_response(1, int(con.data["data"]))

    @asyncio.coroutine
    def _handle_control(self, data):
        """Handles a control request to change fast poll timeout

        :param data: The new fast poll timeout
        :returns: True id the fast poll timeout was changed
        :rtype: Boolean

        """
        v = yield from self._cluster.write_attributes({self._attribute: data})

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True


class PollControlFastPollStop(value.Value):
    """Class to handle the Fast Poll Stop for Poll Control"""
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Stop Fast Poll",
            "permission": value.ValuePermission.WRITE_ONLY,
            "type": "Command",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = 0
        self.data["number"].max = 1
        self.data["number"].step = 1
        self.data["number"].unit = ""

    @asyncio.coroutine
    def _handle_control(self, data=None):
        """Handles a control request to stop fast poll

        :param data: None, no data supported
        :returns: True if the fast poll was stopped
        :rtype: Boolean

        """
        v = yield from self._cluster.fast_poll_stop()

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self._save()
        return True
