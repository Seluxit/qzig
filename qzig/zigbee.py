import asyncio
import logging

import bellows.zigbee.application as zigbee
import bellows.ezsp

LOGGER = logging.getLogger(__name__)


class ZigBee():

    def __init__(self, application, device, databse_file):
        self.app = application
        self.dev = device
        self.db = databse_file

    @asyncio.coroutine
    def connect(self):
        LOGGER.debug("Connecting...")
        s = bellows.ezsp.EZSP()
        yield from s.connect(self.dev)
        LOGGER.debug("Connected")

        LOGGER.debug("Configuring...")
        self.controller = zigbee.ControllerApplication(s, self.db)
        self.controller.add_listener(self.app)
        yield from self.controller.startup(True)
        LOGGER.debug("Configured")

        LOGGER.info("NodeID: %s" % str(self.controller.nwk))
        LOGGER.info("IEEE: %s" % str(self.controller.ieee))

        for ieee, dev in self.controller.devices.items():
            LOGGER.info("Device:")
            LOGGER.info("  NWK: 0x%04x" % (dev._nwk, ))
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
                    clusters = sorted(list(ep.clusters.keys()))
                    if clusters:
                        LOGGER.info("      Clusters:")
                        for cluster in clusters:
                            LOGGER.info("        %s (%s)" % (
                                ep.clusters[cluster].name, cluster
                            ))

    def close(self):
        self.controller._ezsp.close()

    def devices(self):
        return self.controller.devices.items()
