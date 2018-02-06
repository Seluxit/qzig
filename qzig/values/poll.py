import asyncio
import logging

import qzig.value as value
import qzig.state as state

LOGGER = logging.getLogger(__name__)


class PollControlCheckInInterval(value.Value):
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
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
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: data})

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class PollControlLongPollInterval(value.Value):
    _attribute = 1

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
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
    def handle_control(self, data):
        v = yield from self._cluster.set_long_poll_interval(data)

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class PollControlShortPollInterval(value.Value):
    _attribute = 2

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
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
    def handle_control(self, data):
        v = yield from self._cluster.set_short_poll_interval(data)

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class PollControlFastPollTimeout(value.Value):
    _attribute = 3

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
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

    def handle_command(self, aps_frame, tsn, command_id, args):
        if command_id == 0x00:
            con = self.get_state(state.StateType.CONTROL)
            if con.data["data"] == "0":
                self._cluster.checkin_response(0, 0)
            else:
                self._cluster.checkin_response(1, int(con.data["data"]))

    @asyncio.coroutine
    def handle_control(self, data):
        v = yield from self._cluster.write_attributes({self._attribute: data})

        if v[0][0].status == 0:
            self.delayed_report(0, self._attribute, data)
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True


class PollControlFastPollStop(value.Value):
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
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
    def handle_control(self, data=None):
        v = yield from self._cluster.fast_poll_stop()

        if v[1] == 0:
            self.delayed_report(0, self._attribute, v[0])
        else:
            LOGGER.error("%s: %r", self.data["name"], v)
            return False

        self.save()
        return True
