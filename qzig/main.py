#!/usr/bin/env python3

import asyncio
import logging

import qzig.application as application

LOGGER = logging.getLogger(__name__)


def setup_logging():
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


def main():  # pragma: no cover
    setup_logging()

    device = "/dev/ttyACM1"
    database = "qzig.db"

    app = application.Application(device, database)

    # Main event loop
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    try:
        loop.run_until_complete(app.init())
        loop.run_forever()
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Canceling tasks...")
        app.close()
        for task in asyncio.Task.all_tasks():
            task.cancel()

        loop.run_until_complete(asyncio.sleep(.1))
    finally:
        print("Stopping loop")
        loop.close()


if __name__ == "__main__":  # pragma: no cover
    main()
