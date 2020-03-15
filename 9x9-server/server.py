#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from threading import Thread
from signal import signal, SIGINT, SIGTERM
import json

from .client import Client
from .game import Game


class Server:
    def __init__(self, port):
        self.port = port
        self.KILLING = False
        self.thread_num = 1
        self.game = Game()

    def _handler(self, signum, frame):
        print(f'[SIGNAL] Killing by {signum}')
        self.KILLING = True
        self.game.kill()

    def start(self):
        self.old_sigint = signal(SIGINT, self._handler)
        self.old_sigterm = signal(SIGTERM, self._handler)
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s.bind(('', self.port))
        self.s.listen(5)
        self.s.settimeout(5)
        try:
            while not self.KILLING:
                try:
                    (c, addr) = self.s.accept()
                    cc = Client(self.game, c, f'{addr[0]}:{str(addr[1])}')
                    Thread(target=cc.handler, args=(self.thread_num,)).start()
                    self.game.add(cc)
                    self.thread_num += 1
                except timeout:
                    pass
            else:
                print('[MAIN] killed')
        finally:
            self.s.close()
        signal(SIGINT, self.old_sigint)
        signal(SIGTERM, self.old_sigterm)
        print('[MAIN] exitting...')
