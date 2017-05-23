#!/usr/bin/env python3

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
    network_id = "9e32e295-60be-4b9c-91d9-cd7942756496"

    app = application.Application(device, network_id)
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
