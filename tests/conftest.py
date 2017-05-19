import asyncio
import os
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
    db = os.path.join(str(tmpdir), 'test.db')
    app = application.Application(dev, id, db, str(tmpdir))

    bellows.ezsp.EZSP = mock.MagicMock
    bellows.zigbee.application.ControllerApplication = util.ControllerMock

    @asyncio.coroutine
    def rpc_connect(*args, **kwargs):
        rpc = qzig.json_rpc.JsonRPC(app, asyncio.Future())
        rpc.connection_made(mock.MagicMock())
        return rpc

    qzig.json_rpc.connect = rpc_connect

    yield app

    app.close()
