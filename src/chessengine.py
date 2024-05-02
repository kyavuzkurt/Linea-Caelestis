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

        self.enpassantSquares = ()
        self.enpassantSquaresLog = [self.enpassantSquares]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.currentCastlingRightsLog = [CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                                        self.currentCastlingRights.wQs, self.currentCastlingRights.bQs)]
        self.moveLog = []
        self.readableMoveLog = []


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
            self.enpassantSquares = ((move.rowStart + move.rowEnd) // 2, move.colStart)
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
                self.board[move.rowStart][move.colEnd] = move.pieceCaptured
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

    def getValidMoves(self):
        tempCastlingRights = CastleRights(self.currentCastlingRights.wKs, self.currentCastlingRights.bKs,
                                          self.currentCastlingRights.wQs, self.currentCastlingRights.bQs)
        tempEnPassantSquares = self.enpassantSquares
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheckFunction():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        self.currentCastlingRights = tempCastlingRights
        self.enpassantSquares = tempEnPassantSquares

        if len(moves) == 0:
            if self.inCheckFunction():
                self.checkMate = True
            else:
                self.stalemate = True


        return moves

    def inCheckFunction(self):
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
        if self.whiteToMove:
            moveDirection = -1
            doublePush = -2
            enPassantChecker = 2
            startRow = 6
            enemyColor = "b"
        else:
            moveDirection = 1
            doublePush = 2
            enPassantChecker = 5
            startRow = 1
            enemyColor = "w"
        if self.board[r + moveDirection][c] == "--":
            moves.append(Move((r, c), (r + moveDirection, c), self.board))
            if r == startRow and self.board[r + doublePush][c] == "--":
                moves.append(Move((r, c), (r + doublePush , c), self.board))
        if c - 1 >= 0:
            if self.board[r + moveDirection][c - 1][0] == enemyColor:
                moves.append(Move((r,c),(r + moveDirection, c-1), self.board))
            if (r + moveDirection, c -1) == self.enpassantSquares and r + moveDirection == enPassantChecker: #leftside en passant
                moves.append(Move((r,c), (r + moveDirection, c - 1), self.board, isEnpassantMove=True))
        if c + 1 <= 7:
            if self.board[r + moveDirection][c + 1][0] == enemyColor:
                moves.append(Move((r,c),(r + moveDirection, c + 1), self.board))
            if (r + moveDirection, c + 1) == self.enpassantSquares and r + moveDirection == enPassantChecker:
                moves.append(Move((r,c), (r + moveDirection, c + 1), self.board, isEnpassantMove=True))





    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
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
        squares = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        allyColor = "w" if self.whiteToMove else "b"
        for m in squares:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def getBishopMoves(self, r, c, moves):
        diagonals = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in diagonals:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
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
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(len(directions)):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)





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


