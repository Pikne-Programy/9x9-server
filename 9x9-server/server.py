#!/usr/bin/env python3

from asyncio import all_tasks, current_task, gather, get_event_loop as loop, create_task
import websockets
from signal import SIGTERM, SIGINT

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

    async def shutdown(self, sig):
        tasks = [t for t in all_tasks() if t is not current_task()]
        [task.cancel() for task in tasks]
        await gather(*tasks)
        loop().stop()

    def start(self):
        start_server = websockets.serve(self.caught, "", self.port)

        for sig in (SIGTERM, SIGINT):
            loop().add_signal_handler(sig, lambda sig=sig: create_task(self.shutdown(sig)))

        loop().run_until_complete(start_server)
        loop().run_forever()
