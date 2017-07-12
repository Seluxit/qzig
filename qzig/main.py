#!/usr/bin/env python3

import logging
import ssl
import os

import qzig.application as application


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

    device = "/dev/ttyACM2"
    network_id = "9e32e295-60be-4b9c-91d9-cd7942756496"

    baseDir, baseFile = os.path.split(os.path.abspath(__file__))
    certBase = baseDir
    sslServerCert = certBase + "/certificates/ca.crt"
    sslClientCert = certBase + "/certificates/client.crt"
    sslKey = certBase + "/certificates/client.key"

    ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv23)
    ssl_ctx.load_cert_chain(certfile=sslClientCert, keyfile=sslKey)
    ssl_ctx.load_verify_locations(cafile=sslServerCert)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    app = application.Application(device, network_id)
    app.rpc_connection("q-wot.com", 21005, ssl_ctx)
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
