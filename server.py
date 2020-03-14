#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout

from _thread import *
import threading
import json
import time
import sys
import traceback
import signal

print_lock = threading.Lock()

def lprint(*arg, **kwarg):
    print_lock.acquire()
    print(*arg, **kwarg)
    print_lock.release()

class Server:
    def __init__(self, port):
        self.port = port
        self.KILLING = False
    def _handler(self, signum, frame):
        lprint(f'[SIGNAL] Killing {signum} {frame}')
        self.KILLING = True
    def start(self):
        self.old_sigint = signal.signal(signal.SIGINT, self._handler)
        self.old_sigterm = signal.signal(signal.SIGTERM, self._handler)
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s.bind(('', self.port))
        self.s.listen(5)
        self.s.settimeout(5)
        try:
            while not self.KILLING:
                try:
                    (c, addr) = self.s.accept()
                    start_new_thread(self.client_threaded, (c,f'{addr[0]}:{str(addr[1])}'))
                    # TODO: make Thread() and then wait for them (join())
                except timeout:
                    pass
        finally:
            self.s.close()
        signal.signal(signal.SIGINT, self.old_sigint)
        signal.signal(signal.SIGTERM, self.old_sigterm)
    def client_threaded(self, c, addr):
        pre = f'[THREAD {addr}]'
        try:
            c.settimeout(5)
            lprint(pre, 'hello')
            while not self.KILLING:
                try:
                    data = c.recv(2048)
                    if not data:
                        lprint(pre, 'bye')
                        break
                    lprint(f'{pre} got:\n{data}\nEND')
                    json.loads(data)
                    c.send(json.dumps({"status":0,"method":"UIN","params":{"msg":""},"time":int(time.time())}).encode())
                except ConnectionResetError:
                    lprint(f'{pre} connection was reset')
                    break
                except timeout:
                    pass
                except:
                    c.send(json.dumps({"status":0,"method":"ERR","params":{"msg":traceback.format_exc()},"time":int(time.time())}).encode())
            c.send(json.dumps({"status":0,"method":"ERR","params":{"msg":"Server is going down..."},"time":int(time.time())}).encode())
            lprint(f'{pre} server is going down...')
        finally:
            c.close()

PORT = 4780
srv = Server(PORT)
srv.start()
