#!/usr/bin/env python3

import signal


def signalHandler(signal, frame):
    print("Signal %s received, exiting" % str(signal))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
