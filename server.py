#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from _thread import *
import threading
import json
import time
import sys
import traceback

print_lock = threading.Lock()

def lprint(*arg, **kwarg):
    print_lock.acquire()
    print(*arg, **kwarg)
    print_lock.release()

class Server:
    def __init__(self, port):
        self.port = port
    def start(self):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s.bind(('', self.port))
        self.s.listen(5)
        try:
            while True:
                (c, addr) = self.s.accept()
                start_new_thread(self.client_threaded, (c,f'{addr[0]}:{str(addr[1])}'))
        finally:
            self.s.close()
    def client_threaded(self,c, addr):
        pre = f'[THREAD {addr}]'
        try:
            while True:
                try:
                    lprint(pre, "waiting...")
                    data = c.recv(2048)
                    if not data:
                        lprint(pre, 'bye')
                        break
                    lprint(f'{pre} got:\n{data}\nEND')
                    json.loads(data)
                    c.send(json.dumps({"status":0,"method":"UIN","params":{"msg":""},"time":int(time.time())}).encode())
                except:
                    c.send(json.dumps({"status":0,"method":"ERR","params":{"msg":traceback.format_exc()},"time":int(time.time())}).encode())
        finally:
            c.close()

PORT = 4780
srv = Server(PORT)
srv.start()
