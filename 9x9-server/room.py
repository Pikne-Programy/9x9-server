import time


def SendClientMessage(client, message, type):
    client.send({
        "msg": message
    }, type)


class Room:
    def __init__(self, game, id):
        self.board = [[-1 for x in range(9)] for y in range(9)]
        self.boardBig = [[-1 for x in range(3)] for y in range(3)]
        self.clients = []
        self.game = game
        self.id = id
        self.curMove = 0
        self.marked = -1
        self.ready = False
        self.winner = -1

    def Connect(self, client):
        if len(self.clients) == 2:
            return

        self.clients.append(client)

        if len(self.clients) == 2:
            self.Start()

    def Start(self):
        self.ready = True
        for c in self.clients:
            SendClientMessage(c, "connected\n", 'DBG')

    def Move(self, client, x, y):
        if not self.ready:
            SendClientMessage(
                client, "There are not enough players to start the game!\n", "BAD")
            return
        if self.clients[self.curMove] != client:
            SendClientMessage(client, "It isn't your move!\n", "BAD")
            return
        if self.board[x][y] != -1:
            SendClientMessage(client, "This square is not empty! \n", "BAD")
            return

        curSquare = 3*int(y/3) + int(x/3)
        if self.marked != curSquare and self.marked != -1:
            SendClientMessage(client, "Yor move is in wrong big square! \n", "BAD")
            return

        self.board[x][y] = self.curMove

        topLeftX = 3*int(x/3)
        topLeftY = 3*int(y/3)
        b = [[self.board[x1][y1] for x1 in range(topLeftX, topLeftX+3)]
             for y1 in range(topLeftY, topLeftY+3)]
        if self.Check(b):
            self.boardBig[curSquare % 3][int(curSquare/3)] = self.curMove
            if self.Check(self.boardBig):
                self.winner = curMove

        self.marked = 3*(y % 3) + x % 3
        self.curMove = (self.curMove+1) % 2
        self.SendSTTMessage()

    def SendSTTMessage(self):
        character = ["X", "O", "-"]

        sBoard = ""
        for y in range(0, 9):
            for x in range(0, 9):
                sBoard += character[self.board[x][y]]
        sBoardBig = ""
        for y in range(0, 3):
            for x in range(0, 3):
                sBoardBig += character[self.boardBig[x][y]]

        for c in self.clients:
            if c == self.clients[0]:
                you = character[0]
            else:
                you = character[1]

            c.send({
                "status": 0,
                "method": "STT",
                "params": {
                    "board": sBoard,
                    "bigBoard": sBoardBig,
                    "whoWon":  character[self.winner],
                    "you": you,
                    "move": character[self.curMove],
                    "marked": self.marked
                },
                "time": int(time.time())
            })

    def Check(self, b):
        for x1 in range(3):
            if b[0][x1] == b[1][x1] and b[1][x1] == b[2][x1] and b[2][x1] == self.curMove:
                return True
        for y1 in range(3):
            if b[y1][0] == b[y1][1] and b[y1][1] == b[y1][2] and b[y1][2] == self.curMove:
                return True
        if (b[0][0] == b[1][1] and b[1][1] == b[2][2] and b[2][2] == self.curMove) or \
                (b[0][2] == b[1][1] and b[1][1] == b[2][0] and b[2][0] == self.curMove):
            return True
