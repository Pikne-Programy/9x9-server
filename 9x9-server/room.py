import time


class Room:
    def __init__(self, name):
        self.name = name
        self.board = [[-1 for x in range(9)] for y in range(9)]
        self.boardBig = [[-1 for x in range(3)] for y in range(3)]
        self.boardCounter = [0 for s in range(9)]
        self.boardBigCounter = 0
        self.clients = []
        self.curMove = 0
        self.marked = -1
        self.ready = False
        self.winner = -1
        self.lastMove = [None, None]

    async def Connect(self, client):
        if len(self.clients) == 2:
            return

        self.clients.append(client)

        if len(self.clients) == 2:
            await self.Start()

    async def Start(self):
        self.ready = True
        await self.SendSTTMessage()

    async def Move(self, client, x, y):
        if not self.ready:
            await client.send({"msg": "There are not enough players to start the game!\n"}, "BAD")
            return
        if self.winner != -1:
            await client.send({"msg": "The game is over!\n"}, "BAD")
            return
        if self.clients[self.curMove] != client:
            await client.send({"msg": "It isn't your move!\n"}, "BAD")
            return
        if self.board[x][y] != -1:
            await client.send({"msg": "This square is not empty!\n"}, "BAD")
            return

        curSquare = 3*int(y/3) + int(x/3)
        if (self.marked != curSquare and self.marked != -1) or self.boardBig[curSquare % 3][int(curSquare/3)] != -1:
            await client.send({"msg": "Yor move is in wrong big square!\n"}, "BAD")
            return

        self.board[x][y] = self.curMove
        self.boardCounter[curSquare] += 1

        topLeftX = 3*int(x/3)
        topLeftY = 3*int(y/3)
        b = [[self.board[x1][y1] for x1 in range(topLeftX, topLeftX+3)]
             for y1 in range(topLeftY, topLeftY+3)]
        if self.Check(b):
            self.boardBig[curSquare % 3][int(curSquare/3)] = self.curMove
            self.boardBigCounter += 1
            if self.Check(self.boardBig):
                self.winner = self.curMove
            elif self.boardBigCounter == 9:
                # There aren't any empty squares, so the game should end with a draw
                self.winner = -2
        elif self.boardCounter[curSquare] == 9:
            # There is a draw in curSquare
            self.boardBig[self.marked % 3][int(self.marked/3)] = -2
            self.boardBigCounter += 1

        self.marked = 3*(y % 3) + x % 3
        if self.boardBig[self.marked % 3][int(self.marked/3)] != -1:
            self.marked = -1
        self.curMove = (self.curMove+1) % 2
        self.lastMove = [x, y]
        await self.SendSTTMessage()

    async def SendSTTMessage(self):
        character = ["X", "O", "+", "-"]

        sBoard = ""
        for y in range(0, 9):
            for x in range(0, 9):
                sBoard += character[self.board[x][y]]
        sBoardBig = ""
        for y in range(0, 3):
            for x in range(0, 3):
                sBoardBig += character[self.boardBig[x][y]]

        for c in self.clients:
            if c == None:
                continue
            if c == self.clients[0]:
                you = character[0]
            else:
                you = character[1]

            await c.send({
                "board": sBoard,
                "bigBoard": sBoardBig,
                "whoWon":  character[self.winner],
                "you": you,
                "move": character[self.curMove],
                "lastMove": {
                    "x": self.lastMove[0],
                    "y": self.lastMove[1]
                },
                "marked": self.marked
            }, 'STT')

        print({
            "board": sBoard,
            "bigBoard": sBoardBig,
            "whoWon":  character[self.winner],
            "you": you,
            "move": character[self.curMove],
            "lastMove": {
                "x": self.lastMove[0],
                "y": self.lastMove[1]
            },
            "marked": self.marked
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

    async def PlayerDisconnected(self, client):
        if self.ready != True:
            return
        if self.clients[0] == client:
            self.clients[0] = None
            if len(self.clients) == 2:
                self.clients[1].room = None

            if self.winner == -1:
                self.winner = 1
                await self.SendSTTMessage()
        else:
            self.clients[1] = None
            self.clients[0].room = None

            if self.winner == -1:
                self.winner = 0
                await self.SendSTTMessage()
