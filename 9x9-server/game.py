from threading import Lock
from .room import Room

import random


class Game:
    def __init__(self):
        self.clients = []
        self.publicRooms = []
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
            try:
                if client.room.name == "public":
                    self.publicRooms.remove(client.room)
                else:
                    del self.privateRooms[client.room.name]
            except (ValueError, KeyError):
                pass
            finally:
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
            if len(self.publicRooms) == 0 or len(self.publicRooms[0].clients) == 2:
                r = Room(room)
                self.publicRooms.insert(0, r)
            else:
                r = self.publicRooms[0]

            r.Connect(client)
            if len(r.clients) == 2:
                self.publicRooms.insert(0, self.publicRooms.pop(0))
        else:
            try:
                r = self.privateRooms[room]
            except KeyError:
                r = Room(room)
                self.privateRooms[room] = r
            finally:
                r.Connect(client)

        client.room = r

    def set(self, client, x, y):
        if client.room == None:
            client.send({
                "message": "You're not conected to any room!"
            }, "BAD")
            return
        room = client.room

        room.Move(client, x, y)
