from threading import Lock
from .room import Room


import random


def sendRandomState(c):
    # TODO: it's temporary of course and it is there only for testing
    c.send({
        "board": ''.join([random.choice(['X', 'O']+['-']*5) for i in range(9*9)]),
        "bigBoard": ''.join([random.choice(['X', 'O']+['-']*8) for i in range(9)]),
        "whoWon": random.choice(['X', 'O']+['-']*30),
        "you": random.choice(['X', 'O']),
        "move": random.choice(['X', 'O']),
        "marked": random.randint(-1, 8)
    }, 'STT')


class Game:
    def __init__(self):
        self.clients = []
        self.rooms = []
        self.emptyRooms = []
        self.lock = Lock()

    def __del__(self):
        assert len(self.clients) == 0

    def add(self, client):
        self.lock.acquire()
        self.clients += [client]
        self.lock.release()

    def delete(self, client):
        self.lock.acquire()
        if client in self.clients:
            self.clients.remove(client)
            self.lock.release()
        else:
            self.lock.release()
            raise ValueError(client, 'not in clients')

    def kill(self):
        self.KILLING = True
        for c in self.clients:
            c.kill()

    def join(self, client, room):
        if len(self.emptyRooms) == 0:
            r = Room(self, len(self.rooms))
            self.rooms.append(r)
            self.emptyRooms.append(r)
        self.emptyRooms[0].Connect(client)
        client.roomId = self.emptyRooms[0].id

        if len(self.emptyRooms[0].clients) == 2:
            self.emptyRooms.pop(0)
        # sendRandomState(client)

    def set(self, client, x, y):
        print(client.roomId)
        room = self.rooms[client.roomId]
        if not room.ready:
            return

        if room.clients[room.curMove] != client:
            return

        room.Move(x, y)

        # sendRandomState(client)
