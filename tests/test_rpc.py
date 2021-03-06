import asyncio
import tests.util as util
import qzig.state as state

import bellows.zigbee.zcl.clusters.general as general_clusters
from qzig.values import kaercher


def simple_rpc_call(app, cluster, child, value, write_call=1, status=0, child_type=state.StateType.CONTROL):
    app._gateway = None
    devices = util._get_device(cluster)
    util._startup(app, devices)

    dev = next(iter(devices.values()))
    cluster = dev.endpoints[1].in_clusters[cluster]
    cluster._status = status

    s = app._network._children[0]._children[child]._get_state(child_type)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, value)

    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + write_call)
    return app._rpc._transport.write.call_args[0][0].decode()


def failed_rpc_call(app, cluster, child, value="0", write_call=1):
    result = simple_rpc_call(app, cluster, child, value, write_call, 1)
    assert "error" in result


def valid_rpc_call(app, cluster, child, value="0", write_call=2, status=0):
    result = simple_rpc_call(app, cluster, child, value, write_call, status)
    assert "PUT" in result
    assert '"data": "' + str(value) + '"'


def valid_rpc_command_call(app, cluster, child, value="0", write_call=1, status=0):
    result = simple_rpc_call(app, cluster, child, value, write_call, status)
    assert "result" in result
    assert '"data": "' + str(value) + '"'


def result_rpc_call(app, cluster, child, value="0", write_call=1):
    result = simple_rpc_call(app, cluster, child, value, write_call)
    assert "result" in result


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

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/network/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')
    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()

    app._rpc.data_received(b'{"jsonrpc":"2.0","id":"468568996125","method":"GET","params":{"url":"/state/36330a7d-f8c0-4d15-b45f-b092a8f1dbca"}}')
    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()

    d = app._network._children[0]._children[0]
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

    s = app._network._children[0]._children[0]._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0]._children[0]._get_state(state.StateType.CONTROL)
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
    valid_rpc_command_call(app, general_clusters.OnOff.cluster_id, 0)


def test_state_on_change(app):
    valid_rpc_command_call(app, general_clusters.OnOff.cluster_id, 0, "1")


def test_state_on_change_failed(app):
    failed_rpc_call(app, general_clusters.OnOff.cluster_id, 0)


def test_state_on_time_change(app):
    valid_rpc_call(app, general_clusters.OnOff.cluster_id, 1, "1")


def test_state_on_time_change_failed(app):
    failed_rpc_call(app, general_clusters.OnOff.cluster_id, 1)


def test_state_on_timeout_change(app):
    valid_rpc_command_call(app, general_clusters.OnOff.cluster_id, 2)


def test_state_on_timeout_change_failed(app):
    failed_rpc_call(app, general_clusters.OnOff.cluster_id, 2)


def test_state_kaercher_on_timeout_change(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    app._network._children[0].data["manufacturer"] = "Kaercher"

    count = app._rpc._transport.write.call_count

    s = app._network._children[0]._children[2]._get_state(state.StateType.CONTROL)
    assert s is not None
    id = s.id
    rpc = util._rpc_state(id, "1")
    app._rpc.data_received(rpc.encode())

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)

    assert "result" in app._rpc._transport.write.call_args[0][0].decode()


def test_state_report_change(app):
    result = simple_rpc_call(app, general_clusters.OnOff.cluster_id, 0, 0, 1, 0, state.StateType.REPORT)
    assert "error" in result


def test_state_identify_change(app):
    result_rpc_call(app, general_clusters.Identify.cluster_id, 0)


def test_state_poll_check_in_interval_change(app):
    valid_rpc_call(app, general_clusters.PollControl.cluster_id, 0)


def test_state_poll_check_in_interval_change_failed(app):
    failed_rpc_call(app, general_clusters.PollControl.cluster_id, 0)


def test_state_poll_long_interval_change(app):
    valid_rpc_command_call(app, general_clusters.PollControl.cluster_id, 1)


def test_state_poll_long_interval_change_failed(app):
    failed_rpc_call(app, general_clusters.PollControl.cluster_id, 1)


def test_state_poll_short_interval_change(app):
    valid_rpc_command_call(app, general_clusters.PollControl.cluster_id, 2)


def test_state_poll_short_interval_change_failed(app):
    failed_rpc_call(app, general_clusters.PollControl.cluster_id, 2)


def test_state_poll_fast_interval_change(app):
    valid_rpc_call(app, general_clusters.PollControl.cluster_id, 3)


def test_state_poll_fast_interval_change_failed(app):
    failed_rpc_call(app, general_clusters.PollControl.cluster_id, 3)


def test_state_poll_stop_fast_change(app):
    result_rpc_call(app, general_clusters.PollControl.cluster_id, 4)


def test_state_poll_stop_fast_change_failed(app):
    failed_rpc_call(app, general_clusters.PollControl.cluster_id, 4)


def test_reset_all_alarms(app):
    result_rpc_call(app, general_clusters.Alarms.cluster_id, 0)


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

    s = app._network._children[0].get_value(-1, -1)._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0].get_value(-2, -2)._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0].get_value(-2, -2)._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0]._children[1]._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0].get_value(-3, -3)._get_state(state.StateType.CONTROL)
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


def test_gateway_permit_with_only_key_on_old_device(app):
    devices = util._get_device()
    util._startup(app, devices)

    s = app._network._children[0].get_value(-3, -3)._get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "11223344556677884AF7")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()

    dev = next(iter(devices.values()))
    app._zb.controller._cb.device_joined(dev)

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._zb.controller._permit_with_key_count == 1


def test_gateway_permit_with_only_7_bytes_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-3, -3)._get_state(state.StateType.CONTROL)
    assert s is not None

    id = s.id
    rpc = util._rpc_state(id, "28717001506E9E")
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 1)
    assert "error" in app._rpc._transport.write.call_args[0][0].decode()


def test_gateway_permit_with_only_short_key(app):
    util._startup(app)

    s = app._network._children[0].get_value(-3, -3)._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0].get_value(-3, -3)._get_state(state.StateType.CONTROL)
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

    s = app._network._children[0].get_value(-3, -3)._get_state(state.StateType.CONTROL)
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

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()

    assert len((store + "/device").listdir()) == 0


def test_get_value(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    s = app._network._children[0]._children[0]._get_state(state.StateType.REPORT)
    assert s is not None

    id = s.id
    rpc = util._rpc_get("state", id)
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "PUT" in app._rpc._transport.write.call_args[0][0].decode()


def test_get_device(app):
    app._gateway = None
    devices = util._get_device()
    util._startup(app, devices)

    d = app._network._children[0]
    assert d is not None

    id = d.id
    rpc = util._rpc_get("device", id)
    app._rpc.data_received(rpc.encode())

    count = app._rpc._transport.write.call_count

    util.run_loop()

    assert app._rpc._transport.write.call_count == (count + 2)
    assert "result" in app._rpc._transport.write.call_args[0][0].decode()


def test_kaercher_fallback_enable_flag_change(app):
    valid_rpc_call(app, kaercher.KaercherFallback.cluster_id, 0)


def test_kaercher_fallback_enable_flag_change_failed(app):
    failed_rpc_call(app, kaercher.KaercherFallback.cluster_id, 0)


def test_kaercher_fallback_online_flag_change(app):
    valid_rpc_call(app, kaercher.KaercherFallback.cluster_id, 1)


def test_kaercher_fallback_online_flag_change_failed(app):
    failed_rpc_call(app, kaercher.KaercherFallback.cluster_id, 1)


def test_kaercher_fallback_start_time_change(app):
    valid_rpc_call(app, kaercher.KaercherFallback.cluster_id, 2)


def test_kaercher_fallback_start_time_change_failed(app):
    failed_rpc_call(app, kaercher.KaercherFallback.cluster_id, 2)


def test_kaercher_fallback_duration_change(app):
    valid_rpc_call(app, kaercher.KaercherFallback.cluster_id, 3)


def test_kaercher_fallback_duration_change_failed(app):
    failed_rpc_call(app, kaercher.KaercherFallback.cluster_id, 3)


def test_kaercher_fallback_interval_change(app):
    valid_rpc_call(app, kaercher.KaercherFallback.cluster_id, 4)


def test_kaercher_fallback_interval_change_failed(app):
    failed_rpc_call(app, kaercher.KaercherFallback.cluster_id, 4)


def test_ota_notify(app):
    result_rpc_call(app, general_clusters.Ota.cluster_id, 0, "4652-20002-773", 1)


def test_ota_notify_failed(app):
    valid_rpc_call(app, general_clusters.Ota.cluster_id, 0, "4652-20002-773", 2, 1)


def test_ota_notify_invalid_format(app):
    failed_rpc_call(app, general_clusters.Ota.cluster_id, 0, "4652")


def test_ota_notify_invalid_type(app):
    failed_rpc_call(app, general_clusters.Ota.cluster_id, 0, True)
