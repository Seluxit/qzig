import asyncio
import bellows
import json
from unittest import mock

app_devices = {}


class ControllerMock():
    def __init__(self, ezsp, db):
        self._ezsp = ezsp
        self.nwk = 0
        self.ieee = "11:22:33:44:55"
        self.devices = app_devices
        self._cb = None
        self.permit = mock.MagicMock()
        self._permit_with_key_count = 0

    @asyncio.coroutine
    def startup(self, opt):
        pass

    @asyncio.coroutine
    def connect(*args, **kwargs):
        return []

    def add_listener(self, obj):
        self._cb = obj

    @asyncio.coroutine
    def remove(self, obj):
        devices = _get_device()
        dev = next(iter(devices.values()))
        self._cb.device_removed(dev)

    @asyncio.coroutine
    def permit_with_key(self, ieee, installcode, timeout):
        self._permit_with_key_count += 1


class MockDevice():
    def __init__(self, ieee, nwk):
        self.ieee = ieee
        self.nwk = nwk
        self.endpoints = {0: {}}
        self.zdo = MockCluster(0)


class MockEndpoint():
    def __init__(self, endpoint_id):
        self.profile_id = 1
        self.device_type = 1
        self.endpoint_id = endpoint_id
        self.in_clusters = {}
        self.out_clusters = {}
        self.status = bellows.zigbee.endpoint.Status.ZDO_INIT


class MockCluster():
    def __init__(self, id):
        self.name = "Mock"
        self.cluster_id = id
        self._cb = None
        self.reply_count = 0

    @asyncio.coroutine
    def read_attributes(self, *args, **kwargs):
        self.reply_count += 1
        if self.cluster_id == 6:
            return [{0: 0}, 0]
        else:
            if self.reply_count == 1:
                return [{0: 2, 1: 0, 4: b'Kaercher', 5: b'test', 7: 3, 10: b'0'}, 0]
            elif self.reply_count == 2:
                return [0, 1]
            elif self.reply_count == 3:
                return [{0: 2, 1: b'test', 2: b'test', 3: b'test', 4: b'test'}, 0]
            else:
                return None

    @asyncio.coroutine
    def leave(self):
        self._leave = True

    @asyncio.coroutine
    def bind(self, endpoint_id, cluster_id):
        self._bind = True

    @asyncio.coroutine
    def on(self):
        self._on = True
        return [1, 0]

    @asyncio.coroutine
    def off(self):
        self._off = True
        return [0, 0]

    @asyncio.coroutine
    def on_with_timed_off(self, timeout):
        self._timeout = timeout
        return [timeout, 0]

    @asyncio.coroutine
    def identify(self, timeout):
        self._identify = True

    def add_listener(self, obj):
        if self._cb is None:
            self._cb = []
        self._cb.append(obj)

    @asyncio.coroutine
    def dummy(self, *args):
        pass

    def __getattr__(self, *args):
        return self.dummy


def run_loop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.01))


@asyncio.coroutine
def _delayed_reply(app, server_devices):
    yield from asyncio.sleep(0.01)
    data = {
        "type": "urn:seluxit:xml:bastard:device-1.1",
        ":type": "urn:seluxit:xml:bastard:idlist-1.0",
        "id": server_devices
    }
    rpc = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": data
    }
    app._rpc.data_received(json.dumps(rpc).encode())
    yield from asyncio.sleep(0.01)
    app._rpc.data_received(b'{"jsonrpc":"2.0","id":1,"result":true}')


def _startup(app, devs={}, server_devices=[]):
    async_fun = getattr(asyncio, "ensure_future", asyncio.async)
    async_fun(_delayed_reply(app, server_devices))
    global app_devices
    app_devices = devs
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.init())

    assert app._network is not None
    if len(server_devices) == 0:
        if len(devs) == 0 or "device1" in devs:
            assert app._rpc._transport.write.call_count == 2
        else:
            assert app._rpc._transport.write.call_count == 3
        assert app._rpc._pending[0] == -1
    else:
        assert app._rpc._transport.write.call_count == 3


def _get_device(cluster=6):
    endpoint = MockEndpoint(1)
    endpoint.in_clusters[cluster] = MockCluster(cluster)
    device = MockDevice("device1", 1)
    device.endpoints[1] = endpoint
    return {"device1": device}


def _rpc_state(id, data):
    rpc = '{"jsonrpc":"2.0","id":"1","method":"PUT","params":{"url":"/state/' + id + '",'
    rpc += '"data":{"data":"' + str(data) + '","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"' + id + '",":type":"urn:seluxit:xml:bastard:state-1.1"}}}'
    return rpc


def _rpc_delete(type, id):
    rpc = '{"jsonrpc":"2.0","id":"1","method":"DELETE","params":{"url":"/' + type + '/' + id + '"}}'
    return rpc


def _rpc_get(type, id):
    rpc = '{"jsonrpc":"2.0","id":"1","method":"GET","params":{"url":"/' + type + '/' + id + '"}}'
    return rpc
