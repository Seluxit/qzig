import asyncio
import tests.util as util


def test_zigbee_callbacks(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))

    assert app._zb.app._cb is not None

    app._zb.app._cb.device_left(dev)
    app._zb.app._cb.device_joined(dev)
    app._zb.app._cb.device_initialized(dev)
    app._zb.app._cb.attribute_updated(0, 0, 0)


def test_zigbee_zdo_command(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].clusters[6]

    assert cluster._cb is not None

    cluster._cb.zdo_command(0, 0)


def test_zigbee_attribute_update(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].clusters[6]

    assert cluster._cb is not None

    cluster._cb.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_wrong_attribute_update(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].clusters[6]

    assert cluster._cb is not None

    cluster._cb.attribute_updated(1, 0)

    count = app._rpc._transport.write.call_count

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    assert app._rpc._transport.write.call_count == count


def test_zigbee_attribute_update_error_reply(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].clusters[6]

    assert cluster._cb is not None

    cluster._cb.attribute_updated(0, 0)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(.1))

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":1,"error":{"code": -32000, "message": "Test Error"}}')
