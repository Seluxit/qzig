import logging
import os

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
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Ota",
            "string": value.ValueStringType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["string"].max = 50

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
        :param command_id: The command if
        :param args: The arguments for the command

        """
        if command_id == 0x01:
            self._handle_query_next_image(*args)
        elif command_id == 0x03:
            self._handle_image_block(*args)
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
            self._cluster.image_block_response(Status.ABORT, 0, 0, 0, 0, 0)

    def _handle_update_end(self, status, manufacturer_id, image_type, version):
        LOGGER.debug("Update End Request - Status %d Manufactor %s Type %d Version %d", status, manufacturer_id, image_type, version)
        self._cluster.upgrade_end_response(manufacturer_id, image_type, version, 0, 0)
