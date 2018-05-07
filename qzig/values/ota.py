import logging
import os
import asyncio

import qzig.value as value
from bellows.zigbee.zcl.foundation import Status

LOGGER = logging.getLogger(__name__)


class Ota(value.Value):
    """Class to handle OTA messages"""
    _attribute = 6

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self._uuid,
            "name": "Ota",
            "permission": value.ValuePermission.READ_WRITE,
            "type": "Ota",
            "string": value.ValueStringType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["string"].max = 50

    @asyncio.coroutine
    def _handle_control(self, data):
        """Handle OTA control

        Expects data to be in this format: 4652-20002-773
        """
        try:
            data = [int(x) for x in data.split("-")]
            if len(data) != 3:
                return "Invalid data format"
        except Exception:
            return "Invalid data format"

        LOGGER.debug("Sending Image Notify for %s-%s-%s\n", data[0], data[1], data[2])
        payload = 3  # Query jitter, manufacturer code, image type, and new file version
        jitter = 100
        v = yield from self._cluster.image_notify(payload, jitter, data[0], data[1], data[2])

        if v != True:
            LOGGER.error("%s: %r", self.data["name"], v)
            self.delayed_report(0, self._attribute, "Image Notify Error: %r" % v)
            return False

        self._save()
        return True

    def _handle_report(self, attribute, data):
        """Handles incomming OTA reports

        :param attribute: The id of the attribute
        :param data: The OTA report data
        :returns: The OTA report data
        :rtype: Interger

        """
        return data

    def _handle_command(self, aps_frame, tsn, command_id, args):
        """Handles incomming OTA commands

        :param aps_frame: The silabs aps frame
        :param tsn:
        :param command_id: The command id
        :param args: The arguments for the command

        """
        if command_id == 0x01:
            self._handle_query_next_image(*args)
        elif command_id == 0x03:
            self._handle_image_block(*args)
        elif command_id == 0x04:
            self._handle_image_page(*args)
        elif command_id == 0x06:
            self._handle_update_end(*args)

    def _handle_query_next_image(self, control, manufacturer_id, image_type, version, *args):
        info = "Query Next Image Request - Control %d Manufactor Code %d Image Type %d Version %d" % (control, manufacturer_id, image_type, version)
        if control == 1:
            info += " HW %d" % args[0]

        LOGGER.debug(info)

        name = "%d-%d-%d" % (manufacturer_id, image_type, version)
        filename = "ota/%s.upgrade" % name

        try:
            file = open(filename, 'r')
            upgrade = file.read().rstrip()
            new_version = upgrade.split('.')[0].split('-')[2]
            size = os.path.getsize("ota/%s" % upgrade)

            LOGGER.debug("Upgrading %s to %s (%s) size %s", filename, upgrade, new_version, size)

            self.delayed_report(0, self._attribute, "update started (%s)" % name)

            self._cluster.query_next_image_response(Status.SUCCESS, manufacturer_id, image_type, new_version, size)
        except FileNotFoundError:
            self.delayed_report(0, self._attribute, "no image available (%s)" % name)
            LOGGER.warning("Failed to find %s", filename)
            self._cluster.query_next_image_response(Status.NO_IMAGE_AVAILABLE, 0, 0, 0, 0)

    def _handle_image_block(self, control, manufacturer_id, image_type, version, offset, max_size, *args):
        LOGGER.debug("Image Block Request - Control %d Manufactor %d Type %d Version %d Offset %d Max size %d",
                     control, manufacturer_id, image_type, version, offset, max_size)

        filename = "ota/%d-%d-%d.bin" % (manufacturer_id, image_type, version)
        try:
            f = open(filename, "rb")
            f.seek(offset)
            data = f.read(max_size)
            size = len(data)
            f.seek(0, os.SEEK_END)
            total = f.tell()
            progress = int(offset / total * 100)
            self.delayed_report(0, self._attribute, str(progress) + "%")

            LOGGER.debug("Sending OTA Image Block Response frame - Offset %s Size %s", offset, size)
            self._cluster.image_block_response(Status.SUCCESS, manufacturer_id, image_type, version, offset, data)
        except FileNotFoundError:
            LOGGER.error("Failed to load data from file %s", filename)
            self._cluster.image_block_response(Status.NO_IMAGE_AVAILABLE, 0, 0, 0, 0, 0)

    @asyncio.coroutine
    def _send_next_image_block(self):
        LOGGER.debug("Sending next image block from timer")

        if self._page_size <= 0:
            LOGGER.debug("Done sending OTA page")
            return

        # Send the next image block
        self._handle_image_block(0, self._manufacturer_id, self._image_type, self._version, self._offset, self._max_size)

        # Update values with progress
        self._page_size -= self._max_size
        self._offset += self._max_size

        # Start a timer to send the next block
        Timer(self._response_spacing, self._send_next_image_block)

    def _handle_image_page(self, control, manufacturer_id, image_type, version, offset, max_size, page_size, response_spacing, *args):
        LOGGER.debug("Image Page Request - Control %d Manufacturer %d Type %d Version %d Offset %d Max %d Page %d Response %d",
                     control, manufacturer_id, image_type, version, offset, max_size, page_size, response_spacing)

        # Save values
        self._manufacturer_id = manufacturer_id
        self._image_type = image_type
        self._version = version
        self._offset = offset
        self._max_size = max_size
        self._page_size = page_size
        self._response_spacing = response_spacing

        # Start the upload process
        Timer(0, self._send_next_image_block)

    def _handle_update_end(self, status, manufacturer_id, image_type, version):
        LOGGER.debug("Update End Request - Status %d Manufactor %s Type %d Version %d", status, manufacturer_id, image_type, version)
        self._cluster.upgrade_end_response(manufacturer_id, image_type, version, 0, 0)
        self.delayed_report(0, self._attribute, "Update End Status: %d" % status)


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout / 1000
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    @asyncio.coroutine
    def _job(self):
        yield from asyncio.sleep(self._timeout)
        yield from self._callback()
