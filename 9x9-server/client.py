from socket import timeout
from time import time
from threading import Timer
import json
import traceback


def lint_packet(packet):
    warns = ['']
    def a(err, warns=warns):
        warns[0] += err + '\n'

    if packet[-2:] != b'\r\n':
        a('The packet is not ended with \\r\\n')
    obj = None
    try:
        obj = json.loads(packet)
        if 'status' in obj:
            if isinstance(obj['status'], int):
                if obj['status'] != 0:
                    a('The `status` is not 0, are you OK?')
            else:
                a('The `status` is not an integer')
        else:
            a('The packet does not contain a `status`')
        if 'method' in obj:
            if len(obj['method']) != 3:
                a('The `method` does not contain 3 characters')
            if not obj['method'].isalpha():
                a('The `method` is not only letters')
            if not obj['method'].isupper():
                a('The `method` is not uppercase')
        else:
            return None, 'The packet does not contain a `method`'
        if 'params' in obj:
            if not isinstance(obj['params'], dict):
                return None, 'The packet `params` is not an object'
        else:
            return None, 'The packet does not contain `params`'
        if 'time' in obj:
            if isinstance(obj['time'], int):
                if obj['time'] > time():
                    a('The `time` is in future')
                if obj['time'] < time()-60:
                    a('The `time` is later than a minute ago')
            else:
                a('The `time` is not an integer')
        else:
            a('The packet does not contain `time`')
    except json.decoder.JSONDecodeError:
        return None, 'The packet is not valid JSON'
    except:
        return None, traceback.format_exc()
    return obj, warns[0]

PING_EVERY = 120

class Client:
    def __init__(self, game, c, addr):
        self.game = game
        self.c = c
        self.addr = addr
        self.KILLING = False
        self.killed = False
        self.has_thread = False
        self.ping_timer = Timer(PING_EVERY, self.pingit)
        self.ping_timer.start()
        self.last_ping = -1
        self.last_pong = -1
        self.ping = -1
        self.id = '[ANON]'

    def pingit(self):
        if self.last_pong < self.last_ping and (self.last_ping < time() - 30 or PING_EVERY < 30):
            self.ping = -2
            self.send("I can't measure your ping")
            print(self.id+'-pinger ping is not possible')
        self.send({}, 'PNG')
        self.last_ping = time()
        self.ping_timer = Timer(PING_EVERY, self.pingit)
        self.ping_timer.start()
        if self.KILLING:
            self.ping_timer.cancel()

    def kill(self):
        self.KILLING = True
        self.ping_timer.cancel()
        self.ping_timer.join()
        self.ping_timer.cancel()

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
        self.id = f'[THREAD {thread_num}]'
        try:
            self.c.settimeout(5)
            print(self.id, 'hello')
            while not self.KILLING:
                try:
                    data = self.c.recv(2048)
                    if not data:
                        raise ConnectionResetError('not data')
                    print(f'{self.id} got:\n{data}\nEND')
                    obj, lint = lint_packet(data)
                    if obj:
                        self.send(lint, 'DBG')
                        if obj['method'] == 'JON':
                            if 'room' in obj['params']:
                                self.game.join(self, obj['params']['room'])
                            else:
                                self.send('The JON packet does not contain `room`', 'ERR')
                        elif obj['method'] == 'SET':
                            if 'x' in obj['params'] and 'y' in obj['params']:
                                if isinstance(obj['params']['x'], int) and isinstance(obj['params']['y'], int):
                                    if obj['params']['x'] in range(9) and obj['params']['y'] in range(9):
                                        self.game.set(self, obj['params']['x'], obj['params']['y'])
                                    else:
                                        self.send('The `x` and `y` in SET packet should be in range 0..8', 'ERR')
                                else:
                                    self.send('The `x` and `y` in SET packet should be integers', 'ERR')
                            else:
                                self.send('There should be `x` and `y` in SET packet', 'ERR')
                        elif obj['method'] == 'POG':
                            self.last_pong = time()
                            self.ping = self.last_pong - self.last_ping
                            self.send(f"ping={self.ping}")
                            print(f"{self.id} ping: {self.ping}")
                        elif obj['method'] == 'PNG':
                            print(f'{self.id} being pinged')
                            self.send({}, 'POG')
                        else:
                            self.send(f'The `{obj["method"]}` method is not supported', 'UIN')
                    else:
                        self.send(lint, 'ERR')
                except ConnectionResetError as e:
                    print(f'{self.id} connection was reset:', e if e else None)
                    self.kill()
                    break
                except timeout:
                    pass
                except:
                    self.send(traceback.format_exc(), 'ERR')
            else:
                self.send('Server is going down...', 'ERR')
                print(f'{self.id} server is going down...')
        finally:
            self.c.close()
            self.killed = True
            self.game.delete(self)
            self.has_thread = False
