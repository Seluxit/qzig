import asyncio
import tests.util as util
import qzig.state as state


def test_wrong_service(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"PUT","params":{"url":"/wrong/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":"{}"}}')

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_put(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"PUT","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":{"data":"0","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"36330a7d-f8c0-4d15-b45f-b092a8f1dbca",":type":"urn:seluxit:xml:bastard:state-1.1"}}}')

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_post(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"POST","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca","data":{"data":"0","type":"Control","timestamp":"2017-05-19T10:16:28Z",":id":"36330a7d-f8c0-4d15-b45f-b092a8f1dbca",":type":"urn:seluxit:xml:bastard:state-1.1"}}}')

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_get(app):
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/device/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')
    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')
    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()

    d = app._network._children[0]
    assert d is not None
    id = d.id
    rpc = '{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/state/' + id + '"}}'
    app._rpc.data_received(rpc.encode())

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 3)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_wrong_delete(app):
    devices = util._get_device()
    util._startup(app, devices)

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"DELETE","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"DELETE","params":{"url":"/device/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()

    s = app._network._children[0]._children[0].get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = '{"jsonrpc":"2.0","id":"468568996125","method":"DELETE","params":{"url":"/device/' + id + '"}}'
    app._rpc.data_received(rpc.encode())

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 3)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_no_reply(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    s = app._network._children[0]._children[0].get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, "0")
    app._rpc.data_received(rpc.encode())

    @asyncio.coroutine
    def error_off():
        raise Exception("Failed to send")

    s._parent._cluster.off = error_off

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "Failed to send" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_off_change(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    s = app._network._children[0]._children[0].get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, "0")
    app._rpc.data_received(rpc.encode())

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)

    assert "PUT" in app._rpc._transport.write.call_args[0][0].decode()
    assert '"data": "0"' in app._rpc._transport.write.call_args[0][0].decode()


def test_state_on_change(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    s = app._network._children[0]._children[0].get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, "1")
    app._rpc.data_received(rpc.encode())

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)

    assert "PUT" in app._rpc._transport.write.call_args[0][0].decode()
    assert '"data": "1"' in app._rpc._transport.write.call_args[0][0].decode()


def test_state_on_timeout_change(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    s = app._network._children[0]._children[1].get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, "1")
    app._rpc.data_received(rpc.encode())

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)

    assert "PUT" in app._rpc._transport.write.call_args[0][0].decode()
    assert '"data": "10"' in app._rpc._transport.write.call_args[0][0].decode()


def test_state_report_change(app):
    devices = util._get_device()
    util._startup(app, devices)

    s = app._network._children[0]._children[0].get_state(state.StateType.REPORT)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, 0)

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_identify_change(app):
    app._gateway = None
    devices = util._get_device(3)
    util._startup(app, devices)

    s = app._network._children[0]._children[0].get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, 0)

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()


def test_device_change_state(app):
    devices = util._get_device()
    util._startup(app, devices)

    id = app._network._children[1].id
    rpc = util._rpc_state(id, 0)

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit(app):
    util._startup(app)

    s = app._network._children[0].get_value(-1, -1).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, 0)
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 3)
    assert "PUT" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-2, -2).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "00112233445566778899AABBCCDDEEFF1122")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_key_invalid_hex(app):
    util._startup(app)

    s = app._network._children[0].get_value(-2, -2).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "T")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_key_short_hex(app):
    util._startup(app)

    s = app._network._children[0]._children[1].get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "AABB")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_only_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-3, -3).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "11223344556677884AF7")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()

    devices = util._get_device()
    dev = next(iter(devices.values()))
    app._zb.controller._cb.device_joined(dev)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._zb.controller._permit_with_key_count == 1


def test_gateway_permit_with_only_short_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-3, -3).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "1122334455667788")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_only_invalid_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-3, -3).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "1122334455667788JKJK")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_only_wrong_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-3, -3).get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "11223344556677880000")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_delete_device(app, store):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    d = app._network._children[0]
    assert d is not None

    id = d.id
    rpc = util._rpc_delete("device", id)
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()
    assert d._dev.zdo._leave is True

    assert len((store + "/device").listdir()) == 0


def test_get_value(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    s = app._network._children[0]._children[0].get_state(state.StateType.REPORT)
    assert s is not None

    id = s.id
    rpc = util._rpc_get("state", id)
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "PUT" in app._rpc._transport.write.call_args[0][0].decode()
