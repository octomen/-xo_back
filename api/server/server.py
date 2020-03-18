# -*- coding: utf-8 -*-
import asyncio
import logging

import websockets

from websockets.exceptions import ConnectionClosed

from api.server.process import Process, ProcessKey, ProcessStorage

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, router: ProcessStorage):
        self.router = router

    def register_schema(self, schema):
        self.router.register_scope(schema)

    def run(self, host="0.0.0.0", port=8765):
        logger.info(f'Start server: host={host} port={port}')
        start_server = websockets.serve(self.serve_sock, host, port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def serve_sock(self, websocket, path):
        logger.info('New connection with path %s', path)

        info = ProcessKey(websocket, path)
        process = self.router.get(*info.process_key)
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
    async def _handle_recv(info: ProcessKey, router: Process):
        async for message in info.websocket:
            await router.handle_message(message)

    @staticmethod
    async def _ping(info: ProcessKey):
        while True:
            try:
                await asyncio.sleep(1)
                await info.websocket.ping()
            except ConnectionClosed:
                pass


default_server = Server(ProcessStorage())

if __name__ == '__main__':
    server = default_server
    server.run()
