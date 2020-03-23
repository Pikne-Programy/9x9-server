import random


async def sendRandomState(c):
    # TODO: it's temporary of course and it is there only for testing
    await c.send({
        "board": ''.join([random.choice(['X','O']+['-']*5) for i in range(9*9)]),
        "bigBoard": ''.join([random.choice(['X','O']+['-']*8) for i in range(9)]),
        "whoWon": random.choice(['X','O']+['-']*30),
        "you": random.choice(['X','O']),
        "move": random.choice(['X','O']),
        "marked": random.randint(-1,8)
    }, 'STT')

class Game:
    def __init__(self):
        self.clients = []
        self.killed = False

    def __del__(self):
        assert not self.clients

    def add(self, client):
        assert not self.killed
        self.clients += [client]

    def delete(self, client):
        if client in self.clients:
            self.clients.remove(client)
        else:
            raise ValueError(client, 'not in clients')

    async def join(self, client, room):
        await sendRandomState(client)

    async def set(self, client, x, y):
        await sendRandomState(client)

    async def kill(self, msg='The server is going down...'):
        print('[GAME] killing')
        self.killed = True
        [await client.kill(msg) for client in self.clients]
        assert not self.clients
        print('[GAME] killed')
