import asyncio
import logging

import bellows.zigbee.application as zigbee
import bellows.ezsp
import bellows.types as t

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
        self.app = zigbee.ControllerApplication(s, self.db)
        self.app.add_listener(self)
        yield from self.app.startup(True)
        LOGGER.debug("Configured")

        LOGGER.info("NodeID: %s" % str(self.app.nwk))
        LOGGER.info("IEEE: %s" % str(self.app.ieee))

        for ieee, dev in self.app.devices.items():
            LOGGER.info("Device:")
            LOGGER.info("  NWK: 0x%04x" % (dev._nwk, ))
            LOGGER.info("  IEEE: %s" % (ieee, ))
            LOGGER.info("  Endpoints:")
            for epid, ep in dev.endpoints.items():
                if epid == 0:
                    continue
                if ep.status == bellows.zigbee.endpoint.Status.NEW:
                    LOGGER.info("    %s: Uninitialized")
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
        self.app._ezsp.close()

    def devices(self):
        return self.app.devices.items()

    # Callbacks
    def device_left(self, device):
        LOGGER.debug(__name__, device)

    def device_joined(self, device):
        LOGGER.debug(__name__, device)

    def device_initialized(self, device):
        LOGGER.debug(__name__, device)

    def attribute_updated(self, cluster, attrid, value):
        LOGGER.debug(__name__, cluster, attrid, value)
