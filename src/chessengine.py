import chess
import chess.pgn

class ChessBoard:
    def __init__(self):
        self.board = chess.Board()
        self.moveLog = []
        self.readableMoveLog = []


    def makeMove(self, move):
        uci_move = chess.Move.from_uci(move)
        if uci_move in self.board.legal_moves:
            self.board.push(uci_move)
            self.moveLog.append(uci_move)
            self.readableMoveLog.append(self.board.san(uci_move))

    def undoMove(self):
        if len(self.moveLog) != 0:
            self.board.pop()
            self.moveLog.pop()
            self.readableMoveLog.pop()
            self.whiteToMove = not self.whiteToMove

    def getValidMoves(self):
        return list(self.board.legal_moves)

    def inCheckFunction(self):
        return self.board.is_check()

    def isCheckmate(self):
        return self.board.is_checkmate()

    def isStalemate(self):
        return self.board.is_stalemate()

    def isInsufficientMaterial(self):
        return self.board.is_insufficient_material()

    def isGameOver(self):
        return self.board.is_game_over()

    def getBoard(self):
        return self.board

# Example usage
if __name__ == "__main__":
    game = ChessBoard()
    print(game.getBoard())
    game.makeMove("e2e4")
    print(game.getBoard())
    game.undoMove()
    print(game.getBoard())


