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
        self.profile_id = 1
        self.device_type = 1
        self.endpoint_id = endpoint_id
        self.clusters = {}
        self.status = bellows.zigbee.endpoint.Status.ZDO_INIT


class MockCluster():
    def __init__(self, id):
        self.name = "Mock"
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

    @asyncio.coroutine
    def on(self):
        pass

    @asyncio.coroutine
    def off(self):
        pass

    @asyncio.coroutine
    def identify(self, timeout):
        pass


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


def _get_device(cluster=6):
    endpoint = MockEndpoint(1)
    endpoint.clusters[cluster] = MockCluster(cluster)
    device = MockDevice("11:22:33", 1)
    device.endpoints[1] = endpoint
    return {"device1": device}


def _rpc_state(id, data):
    rpc = '{"jsonrpc":"2.0","id":"1","method":"PUT","params":{"url":"/state/' + id + '",'
    rpc += '"data":{"data":"' + str(data) + '","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"' + id + '",":type":"urn:seluxit:xml:bastard:state-1.1"}}}'
    return rpc
