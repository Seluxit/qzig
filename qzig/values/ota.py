import asyncio
import logging
import os

import qzig.value as value
from bellows.zigbee.zcl.foundation import Status

LOGGER = logging.getLogger(__name__)


class Ota(value.Value):
    _attribute = 6

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Ota",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Ota",
            "string": value.ValueStringType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["string"].max = 50

    def handle_command(self, aps_frame, tsn, command_id, args):
        if command_id == 0x01:
            self.handle_query_next_image(*args)
        elif command_id == 0x03:
            self.handle_image_block(*args)
        elif command_id == 0x06:
            self.handle_update_end(*args)

    def handle_query_next_image(self, control, manufacturer_id, image_type, version, *args):
        info = "Query Next Image Request - Control %d Manufactor Code %d Image Type %d Version %d" % (control, manufacturer_id, image_type, version)
        if control == 1:
            info += " HW %d" % args[0]

        LOGGER.debug(info)

        filename = "ota/%d-%d-%d.upgrade" % (manufacturer_id, image_type, version)

        try:
            file = open(filename, 'r')
            upgrade = file.read().rstrip()
            new_version = upgrade.split('.')[0].split('-')[2]
            size = os.path.getsize("ota/%s" % upgrade)

            LOGGER.debug("Upgrading %s to %s (%s) size %s", filename, upgrade, new_version, size)

            self.async_command(self, 'query_next_image_response', Status.SUCCESS, manufacturer_id, image_type, new_version, size)
        except FileNotFoundError:
            LOGGER.warning("Failed to find %s", filename)
            self.async_command(self, 'query_next_image_response', Status.NO_IMAGE_AVAILABLE, 0, 0, 0, 0)

    def handle_image_block(self, control, manufacturer_id, image_type, version, offset, max_size, *args):
        LOGGER.debug("Image Block Request - Control %d Manufactor %d Type %d Version %d Offset %d Max size %d", control, manufacturer_id, image_type, version, offset, max_size)

        filename = "ota/%d-%d-%d.bin" % (manufacturer_id, image_type, version)
        try:
            f = open(filename, "rb")
            f.seek(offset)
            data = f.read(max_size)
            size = len(data)

            LOGGER.debug("Sending OTA Image Block Response frame - Offset %s Size %s", offset, size)
            self.async_command(self, 'image_block_response', Status.SUCCESS, manufacturer_id, image_type, version, offset, data)
        except FileNotFoundError:
            LOGGER.error("Failed to load data from file %s", filename)
            self.async_command(self, 'image_block_response', Status.ABORT, 0, 0, 0, 0, 0)

    def handle_update_end(self, status, manufacturer_id, image_type, version):
        LOGGER.debug("Update End Request - Status %d Manufactor %s Type %d Version %d", status, manufacturer_id, image_type, version)
        self.async_command(self, 'upgrade_end_response', manufacturer_id, image_type, version, 0, 0)

    @asyncio.coroutine
    def send_command(self, args):
        func = args[0]
        args = args[1:]

        yield from self._cluster.__getattr__(func)(*args)
