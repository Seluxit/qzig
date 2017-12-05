import os

import tests.util as util
import bellows.zigbee.zcl.clusters.general as general_clusters
import bellows.zigbee.zcl.clusters.measurement as measurement_clusters
import bellows.zigbee.zcl.clusters.homeautomation as homeautomation_clusters

from qzig.values import kaercher


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
    count = app._rpc._transport.write.call_count

    app._zb.controller._cb.device_joined(dev)

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"PUT"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_device_initialized(app):
    devices = util._get_device()
    endpoint = util.MockEndpoint(2)
    endpoint.in_clusters[general_clusters.OnOff.cluster_id] = util.MockCluster(general_clusters.OnOff.cluster_id)
    devices['00:11:22:33:44:55:66:77'].endpoints[2] = endpoint

    util._startup(app, devices)

    dev = next(iter(devices.values()))

    assert app._zb.controller._cb is not None

    app._zb.controller._cb.device_initialized(dev)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 3)
    assert '"PUT"' in app._rpc._transport.write.call_args[0][0].decode()


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

    cluster.handle_cluster_request(0, 0, 1, (1, 2, 2, 2, 2))
    util.run_loop()

    cluster.handle_cluster_request(0, 0, 3, (1, 2, 2, 2, 0, 50))
    util.run_loop()

    cluster.handle_cluster_request(0, 0, 6, (1, 2, 2, 2))
    util.run_loop()

    os.system("mkdir -p ota")
    os.system("echo 2-2-2.bin > ota/2-2-2.upgrade")
    os.system("dd if=/dev/zero of=ota/2-2-2.bin bs=1M count=1")

    cluster.handle_cluster_request(0, 0, 1, (1, 2, 2, 2, 2))
    util.run_loop()

    cluster.handle_cluster_request(0, 0, 3, (1, 2, 2, 2, 0, 50))
    util.run_loop()

    os.system("rm ota/2-2-2.*")


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


def test_zigbee_power_update(app):
    devices = util._get_device(general_clusters.PowerConfiguration.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.PowerConfiguration.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0x20, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"123456789000"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_poll_update(app):
    devices = util._get_device(general_clusters.PollControl.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.PollControl.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0x0, 1234567890)
        c.attribute_updated(0x1, 1234567890)
        c.attribute_updated(0x2, 1234567890)
        c.attribute_updated(0x3, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 4)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_kaercher_update(app):
    devices = util._get_device(kaercher.KaercherDeviceState.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[kaercher.KaercherDeviceState.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_kaercher_status_update(app):
    devices = util._get_device(kaercher.KaercherDeviceState.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[kaercher.KaercherDeviceState.cluster_id]

    assert cluster._cb is not None

    count = app._rpc._transport.write.call_count

    for c in cluster._cb:
        c.attribute_updated(0, 1)

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    print(app._rpc._transport.write.call_args[0][0].decode())
    assert '"data": "1"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_kaercher_fallback_update(app):
    devices = util._get_device(kaercher.KaercherFallback.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[kaercher.KaercherFallback.cluster_id]

    assert cluster._cb is not None

    for c in cluster._cb:
        c.attribute_updated(0, 1234567890)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert '"1234567890"' in app._rpc._transport.write.call_args[0][0].decode()


def test_zigbee_permit_duration(app):
    devices = util._get_device()
    util._startup(app, devices)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    dev = app._network._children[0]
    dev.permit_duration(1)

    assert app._rpc._transport.write.call_count == count


def test_zigbee_singleton(app):
    devices = util._get_device()
    endpoint1 = util.MockEndpoint(1)
    endpoint2 = util.MockEndpoint(2)
    endpoint1.in_clusters[kaercher.KaercherDeviceState.cluster_id] = util.MockCluster(kaercher.KaercherDeviceState.cluster_id)
    endpoint2.in_clusters[kaercher.KaercherDeviceState.cluster_id] = util.MockCluster(kaercher.KaercherDeviceState.cluster_id)
    devices['00:11:22:33:44:55:66:77'].endpoints[1] = endpoint1
    devices['00:11:22:33:44:55:66:77'].endpoints[2] = endpoint2
    util._startup(app, devices)

    assert len(app._network._children[1]._children) == 4


def test_zigbee_not_singleton(app):
    devices = util._get_device()
    endpoint1 = util.MockEndpoint(1)
    endpoint2 = util.MockEndpoint(2)
    endpoint1.in_clusters[general_clusters.OnOff.cluster_id] = util.MockCluster(general_clusters.OnOff.cluster_id)
    endpoint2.in_clusters[general_clusters.OnOff.cluster_id] = util.MockCluster(general_clusters.OnOff.cluster_id)
    devices['00:11:22:33:44:55:66:77'].endpoints[1] = endpoint1
    devices['00:11:22:33:44:55:66:77'].endpoints[2] = endpoint2
    util._startup(app, devices)

    assert len(app._network._children[1]._children) == 6


def test_zigbee_kaercher_blockage_counter(app):
    devices = util._get_device(general_clusters.OnOff.cluster_id)
    devices['00:11:22:33:44:55:66:77'].endpoints[1].in_clusters[general_clusters.Basic.cluster_id] = util.MockCluster(general_clusters.Basic.cluster_id)
    util._startup(app, devices)

    assert len(app._network._children[1]._children) == 4


def test_zigbee_alarm_update(app):
    devices = util._get_device(general_clusters.Alarms.cluster_id)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[general_clusters.Alarms.cluster_id]

    count = app._rpc._transport.write.call_count

    cluster.handle_cluster_request(0, 0, 0, (0, 1))
    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
