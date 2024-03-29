class ChessBoard:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantSquares = ()
        self.enpassantSquaresLog = [self.enpassantSquares]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.currentCastlingRightsLog = [CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                                        self.currentCastlingRights.wQs, self.currentCastlingRights.bQs)]
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.rowStart][move.colStart] = "--"
        self.board[move.rowEnd][move.colEnd] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.rowEnd, move.colEnd)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.rowEnd, move.colEnd)
        if move.isPawnPromotion:
            self.board[move.rowEnd][move.colEnd] = move.pieceMoved[0] + 'Q' #Only Promotes to a Queen
        if move.isEnpassantMove:
            self.board[move.rowStart][move.colEnd] = "--"
        if move.pieceMoved[1] == 'P' and abs(move.rowStart - move.rowEnd) == 2:
            self.enpassantSquares = ((move.rowStart + move.rowEnd)//2, move.colStart)
        else:
            self.enpassantSquares = ()
        if move.isCastling:
            if move.colEnd - move.colStart == 2: #kingside
                self.board[move.rowEnd][move.colEnd - 1] = self.board[move.rowEnd][move.colEnd + 1]
                self.board[move.rowEnd][move.colEnd + 1] = '--'
            else: #queenside
                self.board[move.rowEnd][move.colEnd + 1] = self.board[move.rowEnd][move.colEnd - 2]
                self.board[move.rowEnd][move.colEnd - 2] = '--'
        self.enpassantSquaresLog.append(self.enpassantSquares)
        self.updateCastlingRights(move)
        self.currentCastlingRightsLog.append(CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                                          self.currentCastlingRights.wQs, self.currentCastlingRights.bQs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.rowStart][move.colStart] = move.pieceMoved
            self.board[move.rowEnd][move.colEnd] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wk":
                self.whiteKingLocation = (move.rowStart, move.colStart)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.rowStart, move.colStart)
            if move.isEnpassantMove:
                self.board[move.rowEnd][move.colEnd] = "--"
                self.board[move.rowStart][move.colStart] = move.pieceCaptured
                self.enpassantSquares = (move.rowEnd, move.colEnd)
            self.enpassantSquaresLog.pop()
            self.enpassantSquares = self.enpassantSquaresLog[-1]
            if move.isCastling:
                if move.colEnd - move.colStart == 2: #kingside
                    self.board[move.rowEnd][move.colEnd + 1] = self.board[move.rowEnd][move.colEnd - 1]
                    self.board[move.rowEnd][move.colEnd - 1] = '--'
                else: #queenside
                    self.board[move.rowEnd][move.colEnd - 2] = self.board[move.rowEnd][move.colEnd + 1]
                    self.board[move.rowEnd][move.colEnd + 1] = '--'
            self.checkMate = False
            self.stalemate = False

    def updateCastlingRights(self, move):
        if move.pieceCaptured == "wR":
            if move.colEnd == 0:
                self.currentCastlingRights.wQs = False
            elif move.colEnd == 7:
                self.currentCastlingRights.wKs = False
        elif move.pieceCaptured == "bR":
            if move.colEnd == 0:
                self.currentCastlingRights.bQs = False
            elif move.colEnd == 7:
                self.currentCastlingRights.bKs = False
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wQs = False
            self.currentCastlingRights.wKs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bQs = False
            self.currentCastlingRights.bKs = False
        elif move.pieceMoved == 'wR':
            if move.rowStart == 7:
                if move.colStart == 0:
                    self.currentCastlingRights.wQs = False
                elif move.colStart == 0:
                    self.currentCastlingRights.wKs = False
        elif move.pieceMoved == 'bR':
            if move.rowStart == 7:
                if move.colStart == 0:
                    self.currentCastlingRights.bQs = False
                elif move.colStart == 0:
                    self.currentCastlingRights.bKs = False

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove((self.pins[i]))
                break

        if self.whiteToMove:
            moveDirection = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveDirection = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation
        if self.board[r + moveDirection][c] == "--":
            if not piecePinned or pinDirection == (moveDirection, 0):
                moves.append(Move((r, c), (r + moveDirection, c), self.board))
                if r == startRow and self.board[r + 2 * moveDirection][c] == "--":
                    moves.append(Move((r, c), (r + 2 * moveDirection, c), self.board))
        if c - 1 >= 0:
            if not piecePinned or pinDirection == (moveDirection, -1):
                if self.board[r + moveDirection][c - 1][0] == enemyColor:
                    moves.append(Move((r,c),(r + moveDirection, c-1), self.board))
                if (r + moveDirection, c -1) == self.enpassantSquares: #leftside en passant
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:
                            insideRange = range(kingCol + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1 ,-1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c), (r + moveDirection, c - 1), self.board, isEnpassantMove=True))
        if c + 1 <= 7:
            if not piecePinned or pinDirection == (moveDirection, +1):
                        if self.board[r + moveDirection][c + 1][0] == enemyColor:
                            moves.append(Move((r,c),(r + moveDirection, c + 1), self.board))
            if (r + moveDirection, c + 1) == self.enpassantSquares:
                attackingPiece = blockingPiece = False
                if kingRow == r:
                    if kingCol < c:
                        insideRange = range(kingCol + 1, c)
                        outsideRange = range(c + 2, 8)
                    else:
                        insideRange = range(kingCol + 1, c)
                        outsideRange = range(c -1, -1, -1)
                    for i in insideRange:
                        if self.board[r][i] != "--":
                            blockingPiece = True
                    for i in outsideRange:
                        square = self.board[r][i]
                        if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                            attackingPiece = True
                        elif square != "--":
                            blockingPiece = True
                if not attackingPiece or blockingPiece:
                    moves.append(Move((r,c), (r + moveDirection, c + 1), self.board, isEnpassantMove=True))





    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])

        squares = ((2, -1), (2, 1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        allyColor = "w" if self.whiteToMove else "b"
        for m in squares:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else:
                        break

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        diagonals = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in diagonals:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKingMoves(self, r, c, moves):
        directions = ((1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (0, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor:
                    if enemyColor == "b":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow, endCol), self.board))
                    if enemyColor == "b":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.whiteToMove and self.currentCastlingRights.wKs) or (not self.whiteToMove and self.currentCastlingRights.bKs):
            self.getKingsideCastlingMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wQs) or (not self.whiteToMove and self.currentCastlingRights.bQs):
            self.getQueensideCastlingMoves(row, col, moves)
    def getKingsideCastlingMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastling = True))
    def getQueensideCastlingMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col -1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col),(row, col - 2), self.board, isCastling = True))

    def getValidMoves(self):
        tempCastlingRights = CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                          self.currentCastlingRights.wQs, self.currentCastlingRights.bQs)

        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].rowEnd, moves[i].colEnd) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.stalemate = True
        else:
            self.checkMate = False
            self.stalemate = False
        self.currentCastlingRights = tempCastlingRights
        return moves


    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.rowEnd == r and move.colEnd == c:
                return True
        return False
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            rowStart = self.whiteKingLocation[0]
            colStart = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            rowStart = self.blackKingLocation[0]
            colStart = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possiblePins = ()
            for i in range (1,8):
                rowEnd = rowStart + direction[0] * i
                colEnd = colStart + direction[1] * i
                if 0 <= rowEnd <= 7 and 0 <= colEnd <= 7:
                    endPiece = self.board[rowEnd][colEnd]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePins == ():
                            possiblePins = (rowEnd, colEnd, direction[0], direction[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        enemyType = endPiece[1]
                        if (0 <= j <= 3 and enemyType == "R") or (4 <= j <= 7 and enemyType == "B") or (i == 1 and enemyType == "P"  and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or (enemyType == "Q") or (i == 1 and enemyType == "K"):
                            if possiblePins == ():
                                inCheck = True
                                checks.append((rowEnd, colEnd, direction[0], direction[1]))
                                break
                            else:
                                pins.append(possiblePins)
                                break
                    else: #no checks
                        break
                else: # off board
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knightMoves:
            rowEnd = rowStart + move[0]
            colEnd = colStart + move[1]
            if 0 <= rowEnd <= 7 and 0 <= colEnd <= 7:
                endPiece = self.board[rowEnd][colEnd]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((rowEnd, colEnd, move[0], move[1]))
        return inCheck, pins, checks



    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

class CastleRights:
    def __init__(self, wKs, bKs, wQs, bQs):
        self.wKs = wKs
        self.wQs = wQs
        self.bQs = bQs
        self.bKs = bKs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsTofiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, sqStart, sqEnd, board, isEnpassantMove=False, isCastling=False):
        self.colStart = sqStart[1]
        self.rowStart = sqStart[0]
        self.colEnd = sqEnd[1]
        self.rowEnd = sqEnd[0]
        self.pieceMoved = board[self.rowStart][self.colStart]
        self.pieceCaptured = board[self.rowEnd][self.colEnd]
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.rowEnd == 0) or (self.pieceMoved == 'bP' and self.rowEnd == 7):
            self.isPawnPromotion = True
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        self.isCastling = isCastling


        self.moveID = self.rowStart * 1000 + self.colStart * 100 + self.rowEnd * 10 + self.colEnd

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.rowStart, self.colStart) + self.getRankFile(self.rowEnd, self.colEnd)

    def getRankFile(self, r, c):
        return self.colsTofiles[c] + self.rowsToRanks[r]


