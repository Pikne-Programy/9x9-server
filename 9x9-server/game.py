from threading import Lock
from .room import Room

import random


class Game:
    def __init__(self):
        self.clients = []
        self.emptyRooms = []
        self.privateRooms = {}
        self.lock = Lock()

    def __del__(self):
        assert len(self.clients) == 0

    def add(self, client):
        self.lock.acquire()
        self.clients += [client]
        self.lock.release()

    def delete(self, client):
        if client.room != None:
            client.room.PlayerDisconnected(client)

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
        if room == "public":
            if len(self.emptyRooms) == 0:
                r = Room()
                self.emptyRooms.append(r)
            else:
                r = self.emptyRooms[0]

            r.Connect(client)
            if len(r.clients) == 2:
                self.emptyRooms.pop(0)
        else:
            try:
                r = self.privateRooms[room]
            except KeyError:
                r = Room()
                self.privateRooms[room] = r
            finally:
                r.Connect(client)
                if len(r.clients) == 2:
                    del self.privateRooms[room]

        client.room = r

    def set(self, client, x, y):
        if client.room == None:
            client.send({
                "message": "You're not conected to any room!"
            }, "BAD")
            return
        room = client.room

        room.Move(client, x, y)
