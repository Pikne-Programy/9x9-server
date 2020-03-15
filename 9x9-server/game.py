from threading import Lock


class Game:
    def __init__(self):
        self.clients = []
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
