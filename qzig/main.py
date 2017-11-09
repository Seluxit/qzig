#!/usr/bin/env python3

import logging
import ssl
import os
import argparse

import qzig.application as application


def setup_logging():
    # set up logging to file
    format = '%(asctime)s %(name)-14s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=format,
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

    parser = argparse.ArgumentParser(description='ZigBee Converter for Seluxit Q platform.')
    parser.add_argument('device', nargs=1, help='The ZigBee serial device')
    parser.add_argument('networkID', nargs='?', default='9e32e295-60be-4b9c-91d9-cd7942756496', help='The network ID that qzig should use')
    args = parser.parse_args()

    device = args.device[0]
    network_id = args.networkID

    base_dir, base_file = os.path.split(os.path.abspath(__file__))
    cert_base = base_dir
    ssl_server_cert = cert_base + "/certificates/ca.crt"
    ssl_client_cert = cert_base + "/certificates/client.crt"
    ssl_key = cert_base + "/certificates/client.key"

    ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv23)
    ssl_ctx.load_cert_chain(certfile=ssl_client_cert, keyfile=ssl_key)
    ssl_ctx.load_verify_locations(cafile=ssl_server_cert)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    app = application.Application(device, network_id, host="q-wot.com", port=21005, ssl=ssl_ctx)
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
