# -*- coding: utf-8 -*-
import asyncio
import logging

import websockets

from websockets.exceptions import ConnectionClosed

from api.server.connection import ConnectionInfo
from api.server.process import Process
from api.server.schema import ISchema

logger = logging.getLogger(__name__)


class Router:
    def __init__(self):
        self.process_type = {}
        self.processes = {}

    def register_schema(self, schema: ISchema):
        self.process_type[schema.get_route()] = schema

    def get_process(self, info: ConnectionInfo) -> Process:
        try:
            router_key = info.get_process_key()
            if router_key not in self.processes[router_key]:
                schema = self.process_type[info.get_process_type()]
                self.processes[router_key] = Process(schema)
            return self.processes[router_key]
        except Exception:
            logger.exception(f'unexpected path form: {info.path}')
            raise


class Server:
    def __init__(self, router: Router):
        self.router = router

    def register_schema(self, schema):
        self.router.register_schema(schema)

    def run(self, host="0.0.0.0", port=8765):
        logger.info(f'Start server: host={host} port={port}')
        start_server = websockets.serve(self.serve_sock, host, port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def serve_sock(self, websocket, path):
        info = ConnectionInfo(websocket, path)
        logger.info('New connection with path %s', info.path)

        process = self.router.get_process(info)
        await process.handle_open(info)
        done, pending = await asyncio.wait(
            [
                self._handle_recv(info, process),
                self._ping(info),
            ], return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()
        await process.handle_close(info)

    @staticmethod
    async def _handle_recv(info: ConnectionInfo, router: Process):
        async for message in info.websocket:
            await router.handle_message(message)

    @staticmethod
    async def _ping(info: ConnectionInfo):
        while True:
            try:
                await asyncio.sleep(1)
                await info.websocket.ping()
            except ConnectionClosed:
                pass


default_server = Server(Router())

if __name__ == '__main__':
    server = default_server
    server.run()
