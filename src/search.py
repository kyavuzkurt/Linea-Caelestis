import chess
import chess.engine
import chess.polyglot
import pickle
from collections import OrderedDict
from evaluation import Evaluation
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import os
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
        if self.stop_search:
            raise KeyboardInterrupt("Search stopped by user.")

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

        if depth == 0 or board.is_game_over():
            evaluation = Evaluation(board)
            score = evaluation.evaluate_board()
            self.debug(f"Leaf node or game over reached, evaluation score: {score}")
            return score

        if isWhite:
            maxEval = -float('inf')
            for move in sorted(board.legal_moves, key=self.move_ordering, reverse=True):
                board.push(move)
                eval = self.alphaBetaSearch(board, depth - 1, alpha, beta, False)
                board.pop()
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.debug("Beta cutoff")
                    break
            flag = EXACT
            if maxEval <= alpha:
                flag = ALPHA
            elif maxEval >= beta:
                flag = BETA
            self.transposition_table[board_fen] = {'value': maxEval, 'depth': depth, 'flag': flag}
            return maxEval
        else:
            minEval = float('inf')
            for move in sorted(board.legal_moves, key=self.move_ordering):
                board.push(move)
                eval = self.alphaBetaSearch(board, depth - 1, alpha, beta, True)
                board.pop()
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    self.debug("Alpha cutoff")
                    break
            flag = EXACT
            if minEval <= alpha:
                flag = ALPHA
            elif minEval >= beta:
                flag = BETA
            self.transposition_table[board_fen] = {'value': minEval, 'depth': depth, 'flag': flag}
            return minEval

    def move_ordering(self, move):
        score = 0
        if self.board.is_capture(move):
            victim = self.board.piece_at(move.to_square).piece_type if self.board.piece_at(move.to_square) else 0
            attacker = self.board.piece_at(move.from_square).piece_type
            score += 10 + victim - attacker  # MVV-LVA heuristic
        if self.board.gives_check(move):
            score += 5
        # Add killer move heuristic or history heuristic here
        return score

    def BestMove(self):
        self.debug("Starting BestMove calculation")
        best_move = None
        best_score = -float('inf') if self.isWhite else float('inf')
        if self.board == chess.Board():
            return chess.Move.from_uci("e2e4")
        
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for current_depth in range(1, self.depth + 1):
                self.debug(f"Starting search at depth {current_depth}")
                futures = {}
                for move in sorted(self.board.legal_moves, key=self.move_ordering, reverse=True):
                    board_copy = self.board.copy(stack=False)
                    board_copy.push(move)
                    futures[executor.submit(self.alphaBetaSearch, board_copy, current_depth - 1, -float('inf'), float('inf'), not self.isWhite)] = move

                for future in as_completed(futures):
                    move = futures[future]
                    try:
                        score = future.result()
                        self.debug(f"Move {move} at depth {current_depth} has score {score}")
                        if (self.isWhite and score > best_score) or (not self.isWhite and score < best_score):
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