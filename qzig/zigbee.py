import asyncio
import logging
import serial
import sys

import bellows.zigbee.application as zigbee
import bellows.ezsp

LOGGER = logging.getLogger(__name__)


class ZigBee():
    """Class to talk to the ZigBee network using bellows"""

    def __init__(self, application, device, database_file):
        """Creates a new ZigBee handler

        :param application: The applition the ZigBee should link with
        :param device: The serial device it should connect to
        :param database_file: The database file where it should store the information about the devices

        """
        self.app = application
        self.dev = device
        self.db = database_file

    @asyncio.coroutine
    def connect(self, baudrate):
        """Connect to the ZigBee using baudrate

        :param baudrate: The baudrate to connect with

        """
        LOGGER.debug("Connecting to ZigBee...")
        s = bellows.ezsp.EZSP()
        try:
            yield from s.connect(self.dev, baudrate)
        except serial.serialutil.SerialException:  # pragma: no cover
            LOGGER.info("Failed to connect to ZigBee on port %s" % self.dev)
            sys.exit(-1)

        LOGGER.debug("Connected to ZigBee")

        LOGGER.debug("Configuring...")
        self.controller = zigbee.ControllerApplication(s, self.db)
        self.controller.add_listener(self.app)
        yield from self.controller.startup(True)
        LOGGER.debug("Configured")

        LOGGER.info("NodeID: %s" % str(self.controller.nwk))
        LOGGER.info("IEEE: %s" % str(self.controller.ieee))

        for ieee, dev in self.controller.devices.items():
            LOGGER.info("Device:")
            LOGGER.info("  NWK: 0x%04x" % (dev.nwk, ))
            LOGGER.info("  IEEE: %s" % (ieee, ))
            LOGGER.info("  Endpoints:")
            for epid, ep in dev.endpoints.items():
                if epid == 0:
                    continue
                if ep.status == bellows.zigbee.endpoint.Status.NEW:
                    LOGGER.info("    %s: Uninitialized")  # pragma: no cover
                else:
                    LOGGER.info(
                        "    %s: profile=0x%02x, device_type=%s" % (
                            epid,
                            ep.profile_id,
                            ep.device_type,
                        )
                    )
                    clusters = sorted(list(ep.in_clusters.keys()))
                    if clusters:
                        LOGGER.info("      Input Clusters:")
                        for cluster in clusters:
                            LOGGER.info("        %s (%s)" % (
                                ep.in_clusters[cluster].name, cluster
                            ))
                    clusters = sorted(list(ep.out_clusters.keys()))
                    if clusters:
                        LOGGER.info("      Output Clusters:")
                        for cluster in clusters:
                            LOGGER.info("        %s (%s)" % (
                                ep.out_clusters[cluster].name, cluster
                            ))

    def close(self):
        """Close the serial connection to ZigBee"""
        self.controller._ezsp.close()

    def devices(self):
        """Get all the devices

        :returns: All the ZigBee devices
        :rtype: Array

        """
        return self.controller.devices.items()

    def ieees(self):
        """Get all the device IEEE

        :returns: All the device IEEE
        :rtype: Array

        """
        return self.controller.devices.keys()
