import asyncio
from unittest import mock

import pytest

import bellows
import qzig.application as application
import qzig

import tests.util as util


@pytest.fixture
def store(tmpdir):
    return tmpdir + "store"


@pytest.fixture
def app(tmpdir):
    dev = "/dev/null"
    id = "test_id"

    app = application.Application(dev, id)
    app.rootdir(str(tmpdir))
    app.rpc_connection(0, 0, 0)

    bellows.ezsp.EZSP = mock.MagicMock
    bellows.zigbee.application.ControllerApplication = util.ControllerMock

    @asyncio.coroutine
    def rpc_connect(*args, **kwargs):
        rpc = qzig.json_rpc.JsonRPC(app, asyncio.Future())
        rpc.connection_made(mock.MagicMock())
        return rpc

    qzig.json_rpc.connect = rpc_connect

    assert app.host == 0
    assert app.port == 0
    assert app.ssl == 0

    yield app

    app.close()
