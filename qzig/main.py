#!/usr/bin/env python3

import signal
import asyncio
import logging

import application as app

LOGGER = logging.getLogger(__name__)


def signalHandler(signal, frame):
    print("Signal %s received, exiting" % str(signal))
    loop = asyncio.get_event_loop()
    loop.stop()
    print("Loop stopped")


def setup_logging():
    #logging.basicConfig(level=logging.DEBUG)
    # set up logging to file
    FORMAT = '%(asctime)s %(name)-14s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%m-%d %H:%M',
                        filename='/tmp/qzig.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-14s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    #logging.getLogger('asyncio').setLevel(logging.DEBUG)


def main():
    #signal.signal(signal.SIGINT, signalHandler)
    #signal.signal(signal.SIGTERM, signalHandler)

    setup_logging()

    device = "/dev/ttyACM1"
    database = "qzig.db"

    a = app.Application(device, database)

    # Main event loop
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    try:
        loop.run_until_complete(a.init())
        LOGGER.debug("Idle loop")
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
