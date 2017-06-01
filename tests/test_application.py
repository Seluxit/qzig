import os
import tests.util as util
from tests.util import MockDevice, MockEndpoint, MockCluster


def test_init(app, tmpdir, store):
    app.gateway(None)
    util._startup(app)

    assert app._zb.controller._cb is not None
    assert len(tmpdir.listdir()) == 0
    assert len(store.listdir()) == 1
    assert str(store.listdir()[0]).endswith("network.json")


def test_only_zigbee_devices(app, store):
    app.gateway(None)
    device = MockDevice("11:22:33", 1)
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1


def test_only_zigbee_device_and_endpoint(app, store):
    app.gateway(None)
    endpoint = MockEndpoint(1)
    device = MockDevice("11:22:33", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 1


def test_zigbee_device_and_endpoint_and_cluster(app, store):
    app.gateway(None)
    devices = util._get_device()
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 1
    assert len(((store + "/device").listdir()[0] + "/value").listdir()[0].listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()[0].listdir()) == 1


def test_zigbee_device_and_endpoint_and_many_cluster(app):
    app.gateway(None)
    endpoint = MockEndpoint(1)
    for c in range(0, 100):
        endpoint.clusters[c] = MockCluster(c)
    endpoint.clusters[0x0402] = MockCluster(0x0402)
    device = MockDevice("11:22:33", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert endpoint.clusters[0]._cb is None
    assert endpoint.clusters[6]._cb is not None


def test_load_json(app, tmpdir, store):
    app.gateway(None)
    data = tmpdir + "/../test_zigbee_device_and_endpoin0store/"
    os.system("cp -rf %s %s" % (data, store))

    devices = util._get_device()
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 1
    assert len(((store + "/device").listdir()[0] + "/value").listdir()[0].listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()[0].listdir()) == 1


def test_wrong_network_data(app, store):
    os.makedirs(str(store))
    store += "/network.json"
    with open(str(store), 'w') as f:
        f.write("WRONG")

    util._startup(app)


def test_disconnect_from_server(app):
    util._startup(app)

    app._rpc.connection_lost(ValueError("Test"))


def test_wrong_devices_from_server(app):
    util._startup(app=app, server_devices=["1"])

    assert "/network/test_id/device/1" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_add(app, store):
    util._startup(app)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1


def test_gateway_load(app, tmpdir, store):
    data = tmpdir + "/../test_gateway_add0store/"
    os.system("cp -rf %s %s" % (data, store))
    util._startup(app)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
