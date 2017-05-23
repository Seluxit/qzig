import asyncio
import tests.util as util


def test_wrong_service(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"PUT","params":{"url":"/wrong/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":"{}"}}')

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_PUT(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"PUT","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":{"data":"0","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"36330a7d-f8c0-4d15-b45f-b092a8f1dbca",":type":"urn:seluxit:xml:bastard:state-1.1"}}}')

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_POST(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"POST","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":{"data":"0","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"36330a7d-f8c0-4d15-b45f-b092a8f1dbca",":type":"urn:seluxit:xml:bastard:state-1.1"}}}')

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_GET(app):
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_DELETE(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"DELETE","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_on_off_change(app):
    devices = util._get_device()
    util._startup(app, devices)

    id = app._network._children[1]._children[0]._children[1].id
    rpc = util._rpc_state(id, "0")

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()

    rpc = util._rpc_state(id, "1")

    app._rpc.data_received(rpc.encode())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_report_change(app):
    devices = util._get_device()
    util._startup(app, devices)

    id = app._network._children[1]._children[0]._children[0].id
    rpc = util._rpc_state(id, 0)

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_identify_change(app):
    devices = util._get_device(3)
    util._startup(app, devices)

    id = app._network._children[1]._children[0]._children[0].id
    rpc = util._rpc_state(id, 0)

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()
