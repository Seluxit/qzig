import asyncio
from unittest import mock

import pytest

import bellows
import qzig.application as application
import qzig


@pytest.fixture
def app():
    dev = "/dev/null"
    db = "test.db"
    app = application.Application(dev, db)

    bellows.ezsp.EZSP = mock.MagicMock()
    con_mock = mock.MagicMock()

    @property
    def devices():
        return [("11:22:33:44:55:66", mock.MagicMock())]

    con_mock.devices = mock.MagicMock()
    con_mock.devices.items = devices
    bellows.zigbee.application.ControllerApplication = con_mock

    rpc_transport = mock.MagicMock()
    connection_future = asyncio.Future()

    rpc = qzig.json_rpc.JsonRPC(app, connection_future)

    @asyncio.coroutine
    def connect(*args, **kwargs):
        return []

    @asyncio.coroutine
    def rpc_connect(*args, **kwargs):
        rpc.connection_made(rpc_transport)
        return rpc

    bellows.zigbee.application.ControllerApplication.connect = connect

    qzig.json_rpc.connect = rpc_connect

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.init())

    assert app._rpc == rpc
    assert rpc._transport == rpc_transport

    # assert app._zb.devices.items.call_count == 1

    yield app

    app.close()


def test_init(app):
    assert app._network is not None


def test_connect(app):
    assert app._rpc._transport.write.call_count == 1

    assert app._rpc._pending[0] == 1
    app._rpc.data_received(b'{"jsonrpc":"2.0","id":1,"result":true}')
    assert app._rpc._pending[0] == -1
