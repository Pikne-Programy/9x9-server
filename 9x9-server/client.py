from socket import timeout
from time import time
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


class Client:
    def __init__(self, game, c, addr):
        self.game = game
        self.roomId = -1
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
                                        self.send(
                                            'The `x` and `y` in SET packet should be in range 0..8', 'ERR')
                                else:
                                    self.send(
                                        'The `x` and `y` in SET packet should be integers', 'ERR')
                            else:
                                self.send('There should be `x` and `y` in SET packet', 'ERR')
                        else:
                            self.send(f'The `{obj["method"]}` method is not supported', 'UIN')
                    else:
                        self.send(lint, 'ERR')
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
