import tests.util as util
import bellows.zigbee.zcl.clusters.general as general_clusters
import bellows.zigbee.zcl.clusters.measurement as measurement_clusters
import bellows.zigbee.zcl.clusters.homeautomation as homeautomation_clusters


def test_zigbee_attribute_update_callback(app):
    devices = util._get_device()
    util._startup(app, devices)

    assert app._zb.controller._cb is not None

    app._zb.controller._cb.attribute_updated(0, 0, 0)


def test_zigbee_device_joined(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))

    assert app._zb.controller._cb is not None

    app._zb.controller._cb.device_joined(dev)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"PUT"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_device_initialized(app):
    devices = util._get_device()
    endpoint = util.MockEndpoint(2)
    endpoint.in_clusters[general_clusters.OnOff.cluster_id] = util.MockCluster(general_clusters.OnOff.cluster_id)
    devices['device1'].endpoints[2] = endpoint

    util._startup(app, devices)

    dev = next(iter(devices.values()))

    assert app._zb.controller._cb is not None

    app._zb.controller._cb.device_initialized(dev)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"POST"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_device_left(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))

    assert app._zb.controller._cb is not None

    app._zb.controller._cb.device_left(dev)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"DELETE"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_device_annoucement(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))

    assert dev.zdo._cb is not None

    for c in dev.zdo._cb:
        c.device_announce(dev)


def test_zigbee_zdo_command(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.OnOff.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.zdo_command(0, 0)


def test_zigbee_input_attribute_update(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.OnOff.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_wrong_attribute_update(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.OnOff.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(1, 0)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == count


def test_zigbee_attribute_update_error_reply(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.OnOff.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 0)

    util.run_loop()

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":1,"error":{"code": -32000, "message": "Test Error"}}')


def test_zigbee_onoff_timeout_update(app):
    devices = util._get_device(general_clusters.OnOff.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.OnOff.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0x42, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_temperature_update(app):
    devices = util._get_device(measurement_clusters.TemperatureMeasurement.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[measurement_clusters.TemperatureMeasurement.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"12345678.9"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_ota_update(app):
    devices = util._get_device(general_clusters.Ota.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.Ota.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.cluster_command(0, 0, 1, (1, 2, 2, 2, 2))

    util.run_loop()

    for c in cluster._cb:
        c.cluster_command(0, 0, 3, (1, 2, 2, 2, 0, 50))

    util.run_loop()

    for c in cluster._cb:
        c.cluster_command(0, 0, 6, (1, 2, 2, 2))

    util.run_loop()


def test_zigbee_humidity_update(app):
    devices = util._get_device(measurement_clusters.RelativeHumidity.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[measurement_clusters.RelativeHumidity.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"12345678.9"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_diagnostics_update(app):
    devices = util._get_device(homeautomation_clusters.Diagnostic.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[homeautomation_clusters.Diagnostic.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0x011D, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_kaercher_update(app):
    devices = util._get_device(0xC001)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[0xC001]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()
