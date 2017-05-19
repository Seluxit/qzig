import tests.util as util


def test_zigbee_callbacks(app):
    devices = util._get_device()
    util._startup(app, devices)

    dev = next(iter(devices.values()))

    app._zb.device_left(dev)
    app._zb.device_joined(dev)
    app._zb.device_initialized(dev)
    app._zb.attribute_updated(0, 0, 0)


def test_zigbee_value_callbacks(app):
    devices = util._get_device()
    util._startup(app, devices)

    value = app._network._children[0]._children[0]

    value.cluster_command(0, 0, 0, 0)
    value.attribute_updated(0, 0)
    value.zdo_command(0, 0)
