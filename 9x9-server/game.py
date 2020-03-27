from .room import Room


class Game:
    def __init__(self):
        self.clients = []
        self.killed = False
        self.publicRooms = []
        self.privateRooms = {}

    def __del__(self):
        assert not self.clients

    def add(self, client):
        assert not self.killed
        self.clients += [client]

    async def delete(self, client):
        if client.room != None:
            try:
                if client.room.name == "public":
                    self.publicRooms.remove(client.room)
                else:
                    del self.privateRooms[client.room.name]
            except (ValueError, KeyError):
                pass
            finally:
                await client.room.PlayerDisconnected(client)
        if client in self.clients:
            self.clients.remove(client)
        else:
            raise ValueError(client, 'not in clients')

    async def kill(self, msg='The server is going down...'):
        print('[GAME] killing')
        self.killed = True
        [await client.kill(msg) for client in self.clients]
        assert not self.clients
        print('[GAME] killed')

    async def join(self, client, room):
        if room == "public":
            if len(self.publicRooms) == 0 or len(self.publicRooms[0].clients) == 2:
                r = Room(room)
                self.publicRooms.insert(0, r)
            else:
                r = self.publicRooms[0]

            await r.Connect(client)
            if len(r.clients) == 2:
                self.publicRooms.insert(0, self.publicRooms.pop(0))
        else:
            try:
                r = self.privateRooms[room]
            except KeyError:
                r = Room(room)
                self.privateRooms[room] = r
            finally:
                await r.Connect(client)

        client.room = r

    async def set(self, client, x, y):
        if client.room == None:
            await client.send({
                "message": "You're not conected to any room!"
            }, "BAD")
            return
        room = client.room

        await room.Move(client, x, y)
