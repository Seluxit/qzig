import os
import shutil
import tests.util as util
from tests.util import MockDevice, MockEndpoint, MockCluster


def test_init(app, tmpdir, store):
    app._gateway = None
    util._startup(app)

    assert app._zb.controller._cb is not None
    assert len(tmpdir.listdir()) == 0
    assert len(store.listdir()) == 1
    assert str(store.listdir()[0]).endswith("network.json")


def test_only_zigbee_devices(app, store):
    app._gateway = None
    device = MockDevice("device1", 1)
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1


def test_only_zigbee_device_and_endpoint(app, store):
    app._gateway = None
    endpoint = MockEndpoint(1)
    device = MockDevice("device1", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 1


def test_zigbee_device_and_endpoint_and_cluster(app, store):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()[0].listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()[0].listdir()) == 1


def test_zigbee_device_and_endpoint_and_many_cluster(app):
    app._gateway = None
    endpoint = MockEndpoint(1)
    for c in range(0, 100):
        endpoint.in_clusters[c] = MockCluster(c)
    for c in range(100, 200):
        endpoint.out_clusters[c] = MockCluster(c)
    endpoint.in_clusters[0x0402] = MockCluster(0x0402)
    device = MockDevice("device1", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert endpoint.in_clusters[0]._cb is None
    assert endpoint.in_clusters[6]._cb is not None


def test_load_json(app, tmpdir, store):
    app._gateway = None
    data = tmpdir + "/../test_zigbee_device_and_endpoin0store/"
    os.system("cp -rf %s %s" % (data, store))

    devices = util._get_device()
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 2
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
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 3


def test_gateway_load(app, tmpdir, store):
    data = tmpdir + "/../test_gateway_add0store/"
    os.system("cp -rf %s %s" % (data, store))

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 3

    util._startup(app)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 3


def test_gateway_load_old(app, tmpdir, store):
    data = tmpdir + "/../test_gateway_add0store/"
    os.system("cp -rf %s %s" % (data, store))

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 3

    path = ((store + "/device").listdir()[0] + "/value").listdir()[0]
    print(path)
    shutil.rmtree(str(path))

    util._startup(app)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 3


def test_remove_deivce_at_boot(app):
    device = MockDevice("device1", 1)
    devices = {"wrong": device}
    util._startup(app, devices)
