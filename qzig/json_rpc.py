import asyncio
import logging
import json

import qzig.util

LOGGER = logging.getLogger(__name__)


class JsonRPC(asyncio.Protocol):

    class Terminator:
        pass

    def __init__(self, app, connected_future=None):
        self._connected_future = connected_future
        self._sendq = asyncio.Queue()
        self._reqq = asyncio.Queue()
        self._app = app
        self._id = 1
        self._pending = (-1, None)

    def connection_made(self, transport):
        """Callback when the socket is connected"""
        self._transport = transport
        if self._connected_future is not None:
            self._connected_future.set_result(True)
        async_fun = getattr(asyncio, "ensure_future", asyncio.async)
        self._task_send = async_fun(self._send_task())
        self._task_request = async_fun(self._request_task())

    def data_received(self, data):
        """Callback when there is data received from the socket"""

        data = data.decode()
        rpc = json.loads(data)
        if "method" in rpc:
            LOGGER.debug("recv: %s", data)
            self._handle_request(rpc)
        else:
            self._handle_result(rpc)

    def connection_lost(self, exc):
        LOGGER.debug("Connection lost")

    def close(self):
        """Close the server connection and queues"""
        self._app = None
        self._sendq.put_nowait(self.Terminator)
        self._task_send.cancel()
        self._reqq.put_nowait(self.Terminator)
        self._task_request.cancel()
        self._transport.close()

    @asyncio.coroutine
    def _send_task(self):
        """Send queue handler"""
        while True:
            item = yield from self._sendq.get()
            if item is self.Terminator:
                break  # pragma: no cover
            data, id, fut = item
            if id is -1:
                self._transport.write(data.encode())
            else:
                self._pending = (id, fut)
                self._transport.write(data.encode())
                if self._pending[1] is not None:
                    yield from self._pending[1]

    def _handle_result(self, rpc):
        pending, self._pending = self._pending, (-1, None)
        if "error" in rpc:
            LOGGER.error(rpc["error"])
            res = rpc["error"]
        else:
            res = rpc["result"]

        if pending[1] is None:
            return
        pending[1].set_result(res)

    def _handle_request(self, rpc):
        self._reqq.put_nowait(rpc)

    @asyncio.coroutine
    def _request_task(self):
        while True:
            item = yield from self._reqq.get()
            if item is self.Terminator:
                break  # pragma: no cover
            LOGGER.debug(item)
            method = item["method"].lower()
            params = item["params"]

            try:
                result = yield from getattr(self._app, method)(**params)
            except Exception as e:
                result = str(e)

            if result is True:
                self._send_result(item["id"], result)
            else:
                LOGGER.error(result)
                self._send_error(item["id"], str(result))

    def _send(self, rpc, id, fut=None):
        LOGGER.debug(json.dumps(rpc,
                                cls=qzig.util.QZigEncoder,
                                sort_keys=True,
                                indent=4,
                                separators=(',', ': ')))
        rpc = json.dumps(rpc, cls=qzig.util.QZigEncoder)
        self._sendq.put_nowait((rpc, id, fut))
        return fut

    def _send_result(self, id, result):
        rpc = {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
        self._send(rpc, -1)

    def _send_error(self, id, error):
        rpc = {
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": -32050,
                "message": error
            }
        }
        self._send(rpc, -1)

    def _rpc(self, method, url, data=None, fut=None):
        id, self._id = self._id, self._id + 1
        rpc = {
            "jsonrpc": "2.0",
            "method": method,
            "id": id,
            "params": {
                "url": url
            }
        }
        if data is not None:
            rpc["params"]["data"] = data

        return self._send(rpc, id, fut)

    @asyncio.coroutine
    def get(self, url):
        fut = asyncio.Future()
        data = yield from self._rpc("GET", url, fut=fut)
        return data

    def post(self, url, data):
        self._rpc("POST", url, data)

    def put(self, url, data):
        self._rpc("PUT", url, data)

    def delete(self, url):
        self._rpc("DELETE", url)


@asyncio.coroutine
def connect(model):  # pragma: no cover
    loop = asyncio.get_event_loop()

    connection_future = asyncio.Future()
    protocol = JsonRPC(model, connection_future)

    yield from loop.create_connection(
        lambda: protocol,
        ssl=model.ssl,
        server_hostname=model.host,
        host=model.host,
        port=model.port
    )

    yield from connection_future

    return protocol
