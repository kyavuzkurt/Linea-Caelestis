import random
import chess
import chess.engine
import chess.polyglot
import chess.syzygy
from advancedEval import evaluate_pawn_structure, evaluate_bishops, evaluate_king_safety, evaluate_piece_mobility
from collections import OrderedDict
import time




pieceScores = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
earlyGamePiecePositionScores = {
    "N": [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
          [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
          [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
          [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
          [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
          [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
          [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
          [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]],
    "B": [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
          [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
          [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
          [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
          [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
          [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
          [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
          [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]],
    "Q": [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
          [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
          [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
          [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
          [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
          [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
          [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
          [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]],
    "R": [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
          [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
          [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
          [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
          [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
          [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
          [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
          [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]],
    "P": [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
          [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
          [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
          [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
          [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
          [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
          [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
          [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]
}

midGamePiecePositionScores = {
    "N": [[-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
          [-0.4, -0.2, 0.0, 0.0, 0.0, 0.0, -0.2, -0.4],
          [-0.3, 0.0, 0.1, 0.15, 0.15, 0.1, 0.0, -0.3],
          [-0.3, 0.05, 0.15, 0.2, 0.2, 0.15, 0.05, -0.3],
          [-0.3, 0.0, 0.15, 0.2, 0.2, 0.15, 0.0, -0.3],
          [-0.3, 0.05, 0.1, 0.15, 0.15, 0.1, 0.05, -0.3],
          [-0.4, -0.2, 0.0, 0.05, 0.05, 0.0, -0.2, -0.4],
          [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5]],
    "B": [[-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2],
          [-0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.1],
          [-0.1, 0.0, 0.05, 0.1, 0.1, 0.05, 0.0, -0.1],
          [-0.1, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05, -0.1],
          [-0.1, 0.0, 0.1, 0.1, 0.1, 0.1, 0.0, -0.1],
          [-0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, -0.1],
          [-0.1, 0.05, 0.0, 0.0, 0.0, 0.0, 0.05, -0.1],
          [-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2]],
    "Q": [[-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2],
          [-0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.1],
          [-0.1, 0.0, 0.05, 0.05, 0.05, 0.05, 0.0, -0.1],
          [-0.05, 0.0, 0.05, 0.05, 0.05, 0.05, 0.0, -0.05],
          [0.0, 0.0, 0.05, 0.05, 0.05, 0.05, 0.0, -0.05],
          [-0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.0, -0.1],
          [-0.1, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, -0.1],
          [-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2]],
    "R": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
          [0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [0.0, 0.0, 0.0, 0.05, 0.05, 0.0, 0.0, 0.0]],
    "P": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
          [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
          [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
          [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15],
          [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
          [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
          [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
          [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35]]
}

endGamePiecePositionScores = {
    "N": [[-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
          [-0.4, -0.2, 0.0, 0.0, 0.0, 0.0, -0.2, -0.4],
          [-0.3, 0.0, 0.1, 0.15, 0.15, 0.1, 0.0, -0.3],
          [-0.3, 0.05, 0.15, 0.2, 0.2, 0.15, 0.05, -0.3],
          [-0.3, 0.0, 0.15, 0.2, 0.2, 0.15, 0.0, -0.3],
          [-0.3, 0.05, 0.1, 0.15, 0.15, 0.1, 0.05, -0.3],
          [-0.4, -0.2, 0.0, 0.05, 0.05, 0.0, -0.2, -0.4],
          [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5]],
    "B": [[-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2],
          [-0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.1],
          [-0.1, 0.0, 0.05, 0.1, 0.1, 0.05, 0.0, -0.1],
          [-0.1, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05, -0.1],
          [-0.1, 0.0, 0.1, 0.1, 0.1, 0.1, 0.0, -0.1],
          [-0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, -0.1],
          [-0.1, 0.05, 0.0, 0.0, 0.0, 0.0, 0.05, -0.1],
          [-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2]],
    "Q": [[-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2],
          [-0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.1],
          [-0.1, 0.0, 0.05, 0.05, 0.05, 0.05, 0.0, -0.1],
          [-0.05, 0.0, 0.05, 0.05, 0.05, 0.05, 0.0, -0.05],
          [0.0, 0.0, 0.05, 0.05, 0.05, 0.05, 0.0, -0.05],
          [-0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.0, -0.1],
          [-0.1, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0, -0.1],
          [-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2]],
    "R": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
          [0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.05],
          [0.0, 0.0, 0.0, 0.05, 0.05, 0.0, 0.0, 0.0]],
    "P": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
          [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
          [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
          [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15],
          [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
          [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
          [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
          [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35]]
}

CHECKMATE = 1000
DRAW = 0
DEPTH = 3  # Change the depth parameter. Max 5 is recommended.
POLYGLOT_FILE = "Titans.bin"  #Using the Titans opening book
SYZYGY_PATH = "/syzygy"  #Using the Syzygy tablebases
FUTILITY_MARGIN = 200
FULL_DEPTH_MOVES = 4
REDUCTION_LIMIT = 3
ASPIRATION_WINDOW = 50
FUTILITY_MARGIN = 200
HISTORY_MAX = 10000
MAX_TIME = 60

# Killer moves and history table
killer_moves = [[None, None] for _ in range(max(DEPTH, 100))]
history_table = [[0 for _ in range(64)] for _ in range(64)]

# Transposition table constants
EXACT = 0
ALPHA = 1
BETA = 2
TT_SIZE = 1000000
tt = OrderedDict()

def tt_store(board, depth, flag, score, best_move):
    global tt
    key = chess.polyglot.zobrist_hash(board)
    tt[key] = TTEntry(key, depth, flag, score, best_move)
    if len(tt) > TT_SIZE:
        tt.popitem(last=False)

def tt_lookup(board):
    key = chess.polyglot.zobrist_hash(board)
    return tt.get(key, None)

class TTEntry:
    def __init__(self, zobrist_hash, depth, flag, score, best_move):
        self.zobrist_hash = zobrist_hash
        self.depth = depth
        self.flag = flag
        self.score = score
        self.best_move = best_move

def bestMove(board, validMoves, returnQueue, time_control):
    global nextMove, nodes_searched
    nextMove = None
    nodes_searched = 0
    start_time = time.time()

    print("DEBUG: Performing optimized search.")
    best_score = -CHECKMATE
    best_move = None

    for depth in range(1, DEPTH + 1):
        if time.time() - start_time > time_control.get('movetime', MAX_TIME):
            break
        
        score = aspirationSearch(board, depth, -CHECKMATE, CHECKMATE, 1 if board.turn else -1)
        
        # Update move ordering based on the latest search
        tt_entry = tt_lookup(board)
        if tt_entry and tt_entry.best_move:
            if score > best_score:
                best_score = score
                best_move = tt_entry.best_move
            print(f"DEBUG: Depth {depth}, Best move: {tt_entry.best_move}, Score: {score}")

    if best_move:
        nextMove = best_move
        print(f"DEBUG: Using search move: {nextMove}")
    else:
        # If no move found, choose the highest scored move
        moveScores = [(move, scoreMove(board, move)) for move in validMoves]
        moveScores.sort(key=lambda x: x[1], reverse=True)
        nextMove = moveScores[0][0]
        print(f"DEBUG: Using highest scored move: {nextMove}")

    print(f"DEBUG: Final best move found: {nextMove}")
    returnQueue.put(nextMove)

    # If no book move or tablebase move, perform the optimized search
    if nextMove is None:
        print("DEBUG: No book or tablebase move found. Performing optimized search.")
        best_score = -CHECKMATE
        for depth in range(1, DEPTH + 1):
            if time.time() - start_time > time_control.get('movetime', MAX_TIME):
                break
            
            score = aspirationSearch(board, depth, -CHECKMATE, CHECKMATE, 1 if board.turn else -1)
            
            # Update move ordering based on the latest search
            tt_entry = tt_lookup(board)
            if tt_entry and tt_entry.best_move:
                if score > best_score:
                    best_score = score
                    nextMove = tt_entry.best_move
                print(f"DEBUG: Depth {depth}, Best move: {tt_entry.best_move}, Score: {score}")

    # If still no move found, choose the highest scored move
    if nextMove is None:
        moveScores = [(move, scoreMove(board, move)) for move in validMoves]
        moveScores.sort(key=lambda x: x[1], reverse=True)
        nextMove = moveScores[0][0]

    print(f"DEBUG: Final best move found: {nextMove}")
    returnQueue.put(nextMove)


def aspirationSearch(board, depth, alpha, beta, color):
    global nextMove
    best_score = -CHECKMATE
    best_move = None
    for move in orderMoves(board, board.legal_moves):
        board.push(move)
        score = -pvs(board, depth - 1, -beta, -alpha, -color, 0)
        board.pop()
        
        if score > best_score:
            best_score = score
            best_move = move
        
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    
    if depth == DEPTH:
        nextMove = best_move
        print(f"DEBUG: Updated nextMove to {best_move} with score {best_score}")
    
    return best_score

def pvs(board, depth, alpha, beta, color, ply):
    global nodes_searched
    nodes_searched += 1
    
    
    # Transposition table lookup
    tt_entry = tt_lookup(board)
    if tt_entry and tt_entry.depth >= depth:
        if tt_entry.flag == EXACT:
            return tt_entry.score
        elif tt_entry.flag == ALPHA and tt_entry.score <= alpha:
            return alpha
        elif tt_entry.flag == BETA and tt_entry.score >= beta:
            return beta
    
    if depth == 0:
        return quiescenceSearch(board, alpha, beta, color)
    
    if board.is_game_over():
        return DRAW if board.is_stalemate() else -CHECKMATE * color
    
    # Null move pruning
    if depth >= 3 and not board.is_check():
        board.push(chess.Move.null())
        nullScore = -pvs(board, depth - 3, -beta, -beta + 1, -color, ply + 1)
        board.pop()
        if nullScore >= beta:
            return beta
    
    # Futility pruning
    if depth <= 2 and abs(alpha) < CHECKMATE - DEPTH:
        staticEval = color * scoreBoard(board)
        if staticEval + FUTILITY_MARGIN * depth <= alpha:
            return quiescenceSearch(board, alpha, beta, color)
    
    moves = orderMoves(board, board.legal_moves)
    bestScore = -CHECKMATE
    bestMove = None
    
    for i, move in enumerate(moves):
        if i == 0:
            board.push(move)
            score = -pvs(board, depth - 1, -beta, -alpha, -color, ply + 1)
            board.pop()
        else:
            board.push(move)
            score = -pvs(board, depth - 1, -alpha - 1, -alpha, -color, ply + 1)
            if alpha < score < beta:
                score = -pvs(board, depth - 1, -beta, -score, -color, ply + 1)
            board.pop()
        
        if score > bestScore:
            bestScore = score
            bestMove = move
        
        alpha = max(alpha, score)
        if alpha >= beta:
            # Update killer moves and history table
            if not board.is_capture(move):
                killer_moves[ply][1] = killer_moves[ply][0]
                killer_moves[ply][0] = move
                history_table[move.from_square][move.to_square] += depth * depth
                if history_table[move.from_square][move.to_square] > HISTORY_MAX:
                    for i in range(64):
                        for j in range(64):
                            history_table[i][j] //= 2
            break
    
    # Store the result in the transposition table
    if bestScore <= alpha:
        flag = ALPHA
    elif bestScore >= beta:
        flag = BETA
    else:
        flag = EXACT
    
    tt_store(board, depth, flag, bestScore, bestMove)
    
    return bestScore

    
def quiescenceSearch(board, alpha, beta, color):
    standPat = color * scoreBoard(board)
    if standPat >= beta:
        return beta
    alpha = max(alpha, standPat)

    moves = [move for move in board.legal_moves if board.is_capture(move)]
    moves = orderMoves(board, moves)

    for move in moves:
        if not board.is_capture(move):
            continue

        board.push(move)
        score = -quiescenceSearch(board, -beta, -alpha, -color)
        board.pop()

        if score >= beta:
            return beta
        alpha = max(alpha, score)

    return alpha

SEE_PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def staticExchangeEvaluation(board, move):
    if not board.is_capture(move):
        return 0

    to_square = move.to_square
    from_square = move.from_square
    piece_type = board.piece_type_at(from_square)
    target_piece_type = board.piece_type_at(to_square)

    if target_piece_type is None:  # En passant capture
        target_piece_type = chess.PAWN
        to_square = to_square + (-8 if board.turn == chess.WHITE else 8)

    gain = SEE_PIECE_VALUES[target_piece_type]
    if gain == 0:
        return 0

    attackers = list(board.attackers(not board.turn, to_square))
    if not attackers:
        return gain

    board.push(move)
    our_attackers = list(board.attackers(board.turn, to_square))
    board.pop()

    if not our_attackers:
        return gain

    gain_list = [gain]
    current_value = SEE_PIECE_VALUES[piece_type]

    while True:
        gain = current_value - gain_list[-1]
        gain_list.append(gain)

        current_value = min((SEE_PIECE_VALUES[board.piece_type_at(sq)] for sq in attackers), default=0)
        if current_value == 0:
            break

        attackers = [sq for sq in attackers if board.piece_type_at(sq) != chess.KING]
        our_attackers = [sq for sq in our_attackers if board.piece_type_at(sq) != chess.KING]

        if not attackers:
            break

        attackers, our_attackers = our_attackers, attackers

    while len(gain_list) > 1:
        gain_list[-2] = -max(-gain_list[-2], gain_list[-1])
        gain_list.pop()

    return gain_list[0]

def orderMoves(board, moves):
    tt_entry = tt_lookup(board)
    tt_move = tt_entry.best_move if tt_entry else None
    
    def moveScore(move):
        if move == tt_move:
            return 1000000
        if board.is_capture(move):
            return 100000 + staticExchangeEvaluation(board, move)
        ply = min(board.ply(), len(killer_moves) - 1)
        if move == killer_moves[ply][0]:
            return 90000
        if move == killer_moves[ply][1]:
            return 80000
        return history_table[move.from_square][move.to_square]
    
    return sorted(moves, key=moveScore, reverse=True)

def scoreMoveOrdering(board, move):
    if board.is_capture(move):
        return 10 + mvv_lva(board, move)
    elif board.gives_check(move):
        return 5
    else:
        return 0

def mvv_lva(board, move):
    if board.is_en_passant(move):
        return 1
    to_piece = board.piece_at(move.to_square)
    from_piece = board.piece_at(move.from_square)
    if to_piece is None or from_piece is None:
        return 0
    return pieceScores[to_piece.symbol().upper()] - pieceScores[from_piece.symbol().upper()] / 100

def scoreMove(board, move):
    board.push(move)
    score = scoreBoard(board)
    board.pop()
    return score

def scoreBoard(board):
    if board.is_checkmate():
        return -CHECKMATE if board.turn else CHECKMATE
    elif board.is_stalemate():
        return DRAW


    totalPieces = len(board.piece_map())
    
    earlyToMidGameWeight = min(1.0, max(0.0, (totalPieces - 28) / 4))  
    midGameWeight = 1.0 - earlyToMidGameWeight
    
    midToEndGameWeight = min(1.0, max(0.0, (totalPieces - 12) / 16)) 
    endGameWeight = 1.0 - midToEndGameWeight

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            pieceType = piece.piece_type
            pieceColor = piece.color
            if pieceType != chess.KING:
                earlyScore = earlyGamePiecePositionScores[chess.PIECE_SYMBOLS[pieceType].upper()][chess.square_rank(square)][chess.square_file(square)]
                midScore = midGamePiecePositionScores[chess.PIECE_SYMBOLS[pieceType].upper()][chess.square_rank(square)][chess.square_file(square)]
                endScore = endGamePiecePositionScores[chess.PIECE_SYMBOLS[pieceType].upper()][chess.square_rank(square)][chess.square_file(square)]
                
                earlyMidScore = earlyScore * earlyToMidGameWeight + midScore * midGameWeight
                piecePositionScore = earlyMidScore * midToEndGameWeight + endScore * endGameWeight
            else:
                piecePositionScore = 0
            
            if pieceColor == chess.WHITE:
                score += pieceScores[chess.PIECE_SYMBOLS[pieceType].upper()] + piecePositionScore
            else:
                score -= pieceScores[chess.PIECE_SYMBOLS[pieceType].upper()] + piecePositionScore
            
        score += evaluate_pawn_structure(board) * 0.5
        score += evaluate_bishops(board) * 0.3
        score += evaluate_king_safety(board) * 0.8
        score += evaluate_piece_mobility(board) * 0.4

    return score
