import asyncio
from unittest import mock

import bellows

app_devices = {}


class ControllerMock():
    def __init__(self, ezsp, db):
        self._ezsp = ezsp
        self.nwk = 0
        self.ieee = "11:22:33:44:55"
        self.devices = app_devices
        print(self.devices)
        self.add_listener = mock.MagicMock()

    @asyncio.coroutine
    def startup(self, opt):
        pass

    @asyncio.coroutine
    def connect(*args, **kwargs):
        return []


class MockDevice():
    def __init__(self, ieee, nwk):
        self.ieee = ieee
        self._nwk = nwk
        self.endpoints = {0: {}}


class MockEndpoint():
    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
        self.clusters = {}
        self.status = bellows.zigbee.endpoint.Status.NEW


class MockCluster():
    def __init__(self, id):
        self.cluster_id = id
        self.add_listener = mock.MagicMock()
        self.reply_count = 0

    @asyncio.coroutine
    def read_attributes(self, *args, **kwargs):
        self.reply_count += 1
        if self.reply_count == 1:
            return [{1: 0, 4: b'test', 5: b'test', 10: b'0'}, 0]
        elif self.reply_count == 2:
            return [0, 1]
        else:
            return None


def _startup(app, devs={}):
    global app_devices
    app_devices = devs
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.init())

    assert app._network is not None
    assert app._rpc._transport.write.call_count == 1

    assert app._rpc._pending[0] == 1
    app._rpc.data_received(b'{"jsonrpc":"2.0","id":1,"result":true}')
    assert app._rpc._pending[0] == -1
