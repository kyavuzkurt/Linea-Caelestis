import chess
import chess.engine
import chess.polyglot
import pickle
from collections import OrderedDict
from evaluation import Evaluation
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
# Transposition table constants
EXACT = 0
ALPHA = 1
BETA = 2
CHECKMATE = -1000

class Search:
    def __init__(self, board: chess.Board, depth: int, isWhite: bool):
        self.depth = depth
        self.board = board
        self.isWhite = isWhite
        self.stop_search = False
        self.transposition_table = {}

    def debug(self, message):
        pass
        #print(f"DEBUG: {message}")

    def alphaBetaSearch(self, board, depth, alpha, beta, isWhite):
        # Transposition table lookup
        board_fen = board.fen()
        if board_fen in self.transposition_table:
            entry = self.transposition_table[board_fen]
            if entry['depth'] >= depth:
                if entry['flag'] == EXACT:
                    return entry['value']
                elif entry['flag'] == ALPHA and entry['value'] <= alpha:
                    return entry['value']
                elif entry['flag'] == BETA and entry['value'] >= beta:
                    return entry['value']

        if self.stop_search or depth == 0 or board.is_game_over():
            evaluation = Evaluation(board)
            score = evaluation.evaluate_board()
            self.debug(f"Leaf node or game over reached, evaluation score: {score}")
            return score

        if isWhite:
            maxEval = -float('inf')
            for move in sorted(board.legal_moves, key=self.move_ordering, reverse=True):
                board.push(move)
                eval = self.alphaBetaSearch(board, depth - 1, alpha, beta, not isWhite)
                board.pop()
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.debug("Beta cutoff")
                    break
            # Store in transposition table
            self.transposition_table[board_fen] = {'value': maxEval, 'depth': depth, 'flag': ALPHA if maxEval <= alpha else BETA if maxEval >= beta else EXACT}
            return maxEval
        else:
            minEval = float('inf')
            for move in sorted(board.legal_moves, key=self.move_ordering):
                board.push(move)
                eval = self.alphaBetaSearch(board, depth - 1, alpha, beta, not isWhite)
                board.pop()
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    self.debug("Alpha cutoff")
                    break
            # Store in transposition table
            self.transposition_table[board_fen] = {'value': minEval, 'depth': depth, 'flag': ALPHA if minEval <= alpha else BETA if minEval >= beta else EXACT}
            return minEval

    def move_ordering(self, move):
        # Simple move ordering heuristic: prioritize captures and checks
        if self.board.is_capture(move):
            return 10
        if self.board.gives_check(move):
            return 5
        return 0

    def BestMove(self):
        self.debug("Starting BestMove calculation")
        best_move = None
        best_score = -float('inf') if self.isWhite else float('inf')
        if self.board == chess.Board():
            best_move = chess.Move.from_uci("e2e4")
        else:
        # Iterative deepening
            for current_depth in range(1, self.depth + 1):
                self.debug(f"Starting search at depth {current_depth}")
                
                with ThreadPoolExecutor() as executor:
                    futures = {}
                    for move in sorted(self.board.legal_moves, key=self.move_ordering, reverse=True):
                        board_copy = self.board.copy()
                        board_copy.push(move)
                        futures[executor.submit(self.alphaBetaSearch, board_copy, current_depth - 1, -float('inf'), float('inf'), not self.isWhite)] = move
                        board_copy.pop()

                    for future in as_completed(futures):
                        move = futures[future]
                        try:
                            score = future.result()
                            self.debug(f"Move {move} at depth {current_depth} has score {score}")
                            if self.isWhite and score > best_score:
                                best_score = score
                                best_move = move
                            elif not self.isWhite and score < best_score:
                                best_score = score
                                best_move = move
                        except Exception as e:
                            self.debug(f"Exception occurred: {e}")

        self.debug(f"Best move: {best_move}, Score: {best_score}")
        return best_move
    
    def RandomMove(self):
        return random.choice(list(self.board.legal_moves))

    def stop(self):
        self.stop_search = True