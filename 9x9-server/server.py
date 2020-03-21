#!/usr/bin/env python3

import asyncio
import websockets

from .client import Client
from .game import Game


class Server:
    def __init__(self, port, updating_command=None, update_cmd=None):
        self.port = port
        self.thread_num = 1
        self.game = Game()
        if updating_command and not update_cmd:
            raise ValueError('update_cmd not specified')
        self.updating_command = updating_command
        self.update_cmd = update_cmd

    async def caught(self, ws, path):
        cc = Client(self, self.game, ws)
        self.game.add(cc)
        self.thread_num += 1
        await cc.handler(self.thread_num)

    def start(self):
        start_server = websockets.serve(self.caught, "", self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
