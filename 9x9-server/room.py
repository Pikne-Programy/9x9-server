class Room:
    def __init__(self, game, id):
        self.board = [[-1 for x in range(9)] for y in range(9)]
        self.clients = []
        self.game = game
        self.id = id
        self.curMove = 0
        self.marked = -1
        self.ready = False

    def Connect(self, client):
        if len(self.clients) == 2:
            return

        self.clients.append(client)

        if len(self.clients) == 2:
            self.Start()

    def Start(self):
        self.ready = True
        for c in self.clients:
            c.send({
                "msg": "connected\n"
            }, 'DBG')

    def Move(self, x, y):
        if not self.ready:
            return
        if self.board[x][y] != -1:
            return

        if self.marked != 3*int(y/3) + int(x/3) and self.marked != -1:
            return

        self.board[x][y] = self.curMove
        if (self.Check(x, y)):
            for c in self.clients:
                c.send({
                    "msg": f"Player {self.curMove} has won square {self.marked}!\n"
                }, 'DBG')

        self.marked = 3*(y % 3) + x % 3
        self.curMove = (self.curMove+1) % 2
        self.clients[self.curMove].send({
            "msg": f"markedSquare: {self.marked}\n"
        }, 'DBG')

    def Check(self, x, y):
        topLeftX = 3*int(x/3)
        topLeftY = 3*int(y/3)
        b = [[self.board[x1][y1] for x1 in range(topLeftX, topLeftX+3)]
             for y1 in range(topLeftY, topLeftY+3)]

        for x1 in range(3):
            if b[0][x1] == b[1][x1] and b[1][x1] == b[2][x1] and b[2][x1] == self.curMove:
                return True
        for y1 in range(3):
            if b[y1][0] == b[y1][1] and b[y1][1] == b[y1][2] and b[y1][2] == self.curMove:
                return True
        if (b[0][0] == b[1][1] and b[1][1] == b[2][2] and b[2][2] == self.curMove) or \
                (b[0][2] == b[1][1] and b[1][1] == b[2][0] and b[2][0] == self.curMove):
            return True

        print(b)
