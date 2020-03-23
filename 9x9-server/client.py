from time import time
import json
import traceback
from subprocess import Popen
from asyncio import CancelledError
from websockets.exceptions import ConnectionClosed


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
    def __init__(self, server, game, ws, client_id):
        self.server = server
        self.game = game
        self.ws = ws
        self.client_id = client_id
        self.pre = f'[CLIENT {client_id}]'

    async def send(self, params, method="DBG", status=0):
        if isinstance(params, str):
            params = {'msg': params}
        obj = {'status': status, 'method': method, 'params': params, 'time': int(time())}
        obj = json.dumps(obj)
        obj += '\r\n'
        await self.ws.send(obj)

    async def kill(self, msg):
        print(f'{self.pre} Disconnecting')
        await self.send('The server is going down...', 'ERR')
        print(f'{self.pre} The server is going down...')
        await self.ws.close()
        self.game.delete(self)

    async def handler(self):
        print(f'{self.pre} hello')
        try:
            async for msg in self.ws:
                try:
                    if self.server.updating_command and self.server.updating_command in msg:
                        print(f'{self.pre} UPDATING COMMAND OCCURED')
                        await self.send('UPDATING COMMAND OCCURED, restarting...', 'ERR')
                        Popen(self.server.update_cmd)
                    print(f'{self.pre} got:\n{msg}\nEND')
                    obj, lint = lint_packet(msg)
                    if obj:
                        await self.send(lint, 'DBG')
                        if obj['method'] == 'JON':
                            if 'room' in obj['params']:
                                await self.game.join(self, obj['params']['room'])
                            else:
                                await self.send('The JON packet does not contain `room`', 'ERR')
                        elif obj['method'] == 'SET':
                            if 'x' in obj['params'] and 'y' in obj['params']:
                                if isinstance(obj['params']['x'], int) and isinstance(obj['params']['y'], int):
                                    if obj['params']['x'] in range(9) and obj['params']['y'] in range(9):
                                        await self.game.set(self, obj['params']['x'], obj['params']['y'])
                                    else:
                                        await self.send('The `x` and `y` in SET packet should be in range 0..8', 'ERR')
                                else:
                                    await self.send('The `x` and `y` in SET packet should be integers', 'ERR')
                            else:
                                await self.send('There should be `x` and `y` in SET packet', 'ERR')
                        else:
                            await self.send(f'The `{obj["method"]}` method is not supported', 'UIN')
                    else:
                        print(lint)
                        await self.send(lint, 'ERR')
                except CancelledError:
                    break
                except:
                    print(traceback.format_exc())
                    await self.send(traceback.format_exc(), 'ERR')
        except ConnectionClosed:
            print(f'{self.pre} connection was closed')
        print(f'{self.pre} bye')
