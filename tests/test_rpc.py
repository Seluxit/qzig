import os
import asyncio
import tests.util as util
from tests.util import MockDevice, MockEndpoint, MockCluster


def test_PUT(app):
    util._startup(app)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"PUT","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":{"data":"0","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"36330a7d-f8c0-4d15-b45f-b092a8f1dbca",":type":"urn:seluxit:xml:bastard:state-1.1"}}}')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == 2


def test_POST(app):
    util._startup(app)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"POST","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":{"data":"0","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"36330a7d-f8c0-4d15-b45f-b092a8f1dbca",":type":"urn:seluxit:xml:bastard:state-1.1"}}}')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == 2


def test_GET(app):
    util._startup(app)

    assert app._rpc._transport.write.call_count == 1

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == 2


def test_DELETE(app):
    util._startup(app)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"DELETE","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == 2
