from socket import timeout
from time import time
import json
import traceback


class Client:
    def __init__(self, game, c, addr):
        self.game = game
        self.c = c
        self.addr = addr
        self.KILLING = False
        self.killed = False
        self.has_thread = False

    def kill(self):
        self.KILLING = True

    def send(self, params, method="DBG", status=0):
        if isinstance(params, str):
            params = {'msg': params}
        obj = {'status': status, 'method': method, 'params': params, 'time': int(time())}
        obj = json.dumps(obj)
        obj += '\r\n'
        obj = obj.encode()
        self.c.send(obj)

    def handler(self, thread_num):
        assert self.has_thread == False
        self.has_thread = True
        pre = f'[THREAD {thread_num}]'
        try:
            self.c.settimeout(5)
            print(pre, 'hello')
            while not self.KILLING:
                try:
                    data = self.c.recv(2048)
                    if not data:
                        print(pre, 'bye')
                        break
                    print(f'{pre} got:\n{data}\nEND')
                    json.loads(data)
                    self.send('', 'UIN')
                except ConnectionResetError:
                    print(f'{pre} connection was reset')
                    break
                except timeout:
                    pass
                except:
                    self.send(traceback.format_exc(), 'ERR')
            else:
                self.send('Server is going down...', 'ERR')
                print(f'{pre} server is going down...')
        finally:
            self.c.close()
            self.killed = True
            self.game.delete(self)
            self.has_thread = False
