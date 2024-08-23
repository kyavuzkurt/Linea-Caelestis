#bin/bash/python3
import chess
import chess.engine
import sys
from search import Search

class UCIWrapper:
    def __init__(self, verbose=False):
        self.board = chess.Board()
        self.engine = None
        self.search = None
        self.verbose = verbose

    def debug(self, message):
        if self.verbose:
            print(f"DEBUG: {message}")

    def uci(self):
        self.debug("Received 'uci' command")
        print("id name Linea Caelestis")
        print("id author Kadir Yavuz Kurt")
        print("uciok")

    def isready(self):
        self.debug("Received 'isready' command")
        print("readyok")

    def ucinewgame(self):
        self.debug("Received 'ucinewgame' command")
        self.board = chess.Board()

    def position(self, command):
        self.debug(f"Received 'position' command: {command}")
        tokens = command.split()
        if 'startpos' in tokens:
            self.board.set_fen(chess.STARTING_FEN)
            moves_index = tokens.index('moves') + 1 if 'moves' in tokens else len(tokens)
        elif 'fen' in tokens:
            fen_index = tokens.index('fen') + 1
            fen = ' '.join(tokens[fen_index:fen_index + 6])
            self.board.set_fen(fen)
            moves_index = tokens.index('moves') + 1 if 'moves' in tokens else len(tokens)
        else:
            moves_index = len(tokens)

        for move in tokens[moves_index:]:
            self.debug(f"Applying move: {move}")
            self.board.push_uci(move)

    def go(self):
        self.debug("Received 'go' command")
        depth = 10
        self.debug(f"Initializing search with depth {depth}")
        self.search = Search(self.board, depth, self.board.turn == chess.WHITE)
        best_move = self.search.BestMove()
        if best_move not in self.board.legal_moves:
            best_move = self.search.RandomMove()
        if best_move:
            self.debug(f"Best move found: {best_move.uci()}")
            print(f"bestmove {best_move.uci()}")
        else:
            self.debug("No best move found")

    def stop(self):
        self.debug("Received 'stop' command")
        if self.search:
            self.search.stop()
            print("Search stopped")

    def loop(self):
        self.debug("Entering main loop")
        while True:
            command = input().strip()
            self.debug(f"Received command: {command}")
            if command == 'uci':
                self.uci()
            elif command == 'isready':
                self.isready()
            elif command == 'ucinewgame':
                self.ucinewgame()
            elif command.startswith('position'):
                self.position(command)
            elif command.startswith('go'):
                self.go()
            elif command == 'stop':
                self.stop()
            elif command == 'quit':
                self.debug("Received 'quit' command")
                break

if __name__ == "__main__":
    verbose = '-v' in sys.argv
    UCIWrapper(verbose).loop()