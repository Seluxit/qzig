import asyncio
import logging
import sys
import os
import ssl
import json

import qzig.util

LOGGER = logging.getLogger(__name__)

baseDir, baseFile = os.path.split(os.path.abspath(__file__))
certBase = baseDir
sslServerCert = certBase + "/certificates/ca.crt"
sslClientCert = certBase + "/certificates/client.crt"
sslKey = certBase + "/certificates/client.key"


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
        if sys.version_info >= (3, 5):
            self._task_send = asyncio.ensure_future(self._send_task())
            self._task_request = asyncio.ensure_future(self._request_task())
        else:  # pragma: no cover
            self._task_send = asyncio.async(self._send_task())
            self._task_request = asyncio.async(self._request_task())

    def data_received(self, data):
        """Callback when there is data received from the socket"""

        data = data.decode()
        LOGGER.debug("recv: %s", data)

        rpc = json.loads(data)
        if "method" in rpc:
            self._handle_request(rpc)
        else:
            self._handle_result(rpc)

    def connection_lost(self, exc):
        if self._app is not None:
            print("Connection lost, reconnect...")

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
            data, id = item
            if id is -1:
                self._transport.write(data.encode())
            else:
                self._pending = (id, asyncio.Future())
                self._transport.write(data.encode())
                yield from self._pending[1]

    def _handle_result(self, rpc):
        pending, self._pending = self._pending, (-1, None)

        if "error" in rpc:
            LOGGER.error(rpc["error"])
            pending[1].set_result(False)
        else:
            pending[1].set_result(True)

    def _handle_request(self, rpc):
        self._reqq.put_nowait(rpc)

    @asyncio.coroutine
    def _request_task(self):
        while True:
            item = yield from self._reqq.get()
            if item is self.Terminator:
                break  # pragma: no cover
            LOGGER.debug(item)
            method = item["method"]
            params = item["params"]
            result = yield from getattr(self._app, method)(**params)
            if result is True:
                self._send_result(item["id"], result)
            else:
                LOGGER.error(result)
                self._send_error(item["id"], str(result))

    def _send(self, rpc, id):
        LOGGER.debug(json.dumps(rpc,
                                cls=qzig.util.QZigEncoder,
                                sort_keys=True,
                                indent=4,
                                separators=(',', ': ')))
        rpc = json.dumps(rpc, cls=qzig.util.QZigEncoder)
        self._sendq.put_nowait((rpc, id))

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

    def _rpc(self, method, url, data):
        id = self._id
        self._id = self._id + 1
        rpc = {
            "jsonrpc": "2.0",
            "method": method,
            "id": id,
            "params": {
                "url": url,
                "data": data
            }
        }
        self._send(rpc, id)

    def post(self, url, data):
        return self._rpc("POST", url, data)


@asyncio.coroutine
def connect(model):  # pragma: no cover
    loop = asyncio.get_event_loop()

    connection_future = asyncio.Future()
    protocol = JsonRPC(model, connection_future)

    ssl_ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv23)
    ssl_ctx.load_cert_chain(certfile=sslClientCert, keyfile=sslKey)
    ssl_ctx.load_verify_locations(cafile=sslServerCert)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    host = "q-wot.com"
    port = 21005

    yield from loop.create_connection(
        lambda: protocol,
        ssl=ssl_ctx,
        server_hostname=host,
        host=host,
        port=port
    )

    yield from connection_future

    return protocol
