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

    def kill(self):
        self.KILLING = True

    def handler(self, thread_num):
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
                    self.c.send(json.dumps({"status":0,"method":"UIN","params":{"msg":""},"time":int(time())}).encode())
                except ConnectionResetError:
                    print(f'{pre} connection was reset')
                    break
                except timeout:
                    pass
                except:
                    self.c.send(json.dumps({"status":0,"method":"ERR","params":{"msg":traceback.format_exc()},"time":int(time())}).encode())
            else:
                self.c.send(json.dumps({"status":0,"method":"ERR","params":{"msg":"Server is going down..."},"time":int(time())}).encode())
                print(f'{pre} server is going down...')
        finally:
            self.c.close()
            self.killed = True
            self.game.delete(self)
