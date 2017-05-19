import os
import tests.util as util
from tests.util import MockDevice, MockEndpoint, MockCluster


def test_init(app, tmpdir, store):
    util._startup(app)

    assert app._zb.app.add_listener.call_count == 1
    assert len(tmpdir.listdir()) == 0
    assert len(store.listdir()) == 1
    assert str(store.listdir()[0]).endswith("network.json")


def test_only_zigbee_devices(app, store):
    device = MockDevice("11:22:33", 1)
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1


def test_only_zigbee_device_and_endpoint(app, store):
    endpoint = MockEndpoint(1)
    device = MockDevice("11:22:33", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 1


def test_zigbee_device_and_endpoint_and_cluster(app, store):
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
    endpoint = MockEndpoint(1)
    for c in range(0, 100):
        endpoint.clusters[c] = MockCluster(c)
    endpoint.clusters[0x0402] = MockCluster(0x0402)
    device = MockDevice("11:22:33", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert endpoint.clusters[0].add_listener.call_count == 0
    assert endpoint.clusters[6].add_listener.call_count == 1


def test_load_json(app, tmpdir, store):
    data = tmpdir + "/../test_zigbee_device_and_endpoin0store/"
    os.system("cp -rf %s %s" % (data, store))

    endpoint = MockEndpoint(1)
    endpoint.clusters[6] = MockCluster(6)
    device = MockDevice("11:22:33", 1)
    device.endpoints[1] = endpoint
    devices = {"device1": device}
    util._startup(app, devices)

    assert len(store.listdir()) == 2
    assert len((store + "/device").listdir()) == 1
    assert len((store + "/device").listdir()[0].listdir()) == 2
    assert len(((store + "/device").listdir()[0] + "/value").listdir()) == 1
    assert len(((store + "/device").listdir()[0] + "/value").listdir()[0].listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()) == 2
    assert len((((store + "/device").listdir()[0] + "/value").listdir()[0] + "/state").listdir()[0].listdir()) == 1


def test_disconnect_from_server(app):
    util._startup(app)

    app._rpc.connection_lost(ValueError("Test"))
