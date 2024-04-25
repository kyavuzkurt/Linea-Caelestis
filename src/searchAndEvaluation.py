import random
pieceScores = {"K": 0, "Q":9, "R":5, "B":3, "N":3, "P":1}
knightScores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishopScores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rookScores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
              [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queenScores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
               [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
               [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
               [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
               [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
               [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
               [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
               [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawnScores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
              [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
              [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
              [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
              [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
              [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
              [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
              [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piecePositionScores = {"wN": knightScores,
                         "bN": knightScores[::-1],
                         "wB": bishopScores,
                         "bB": bishopScores[::-1],
                         "wQ": queenScores,
                         "bQ": queenScores[::-1],
                         "wR": rookScores,
                         "bR": rookScores[::-1],
                         "wP": pawnScores,
                         "bP": pawnScores[::-1]}
CHECKMATE = 1000
DRAW = 0
DEPTH = 2
def randomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def bestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return DRAW
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != "--":
                piecePositionScore = 0
                if piece[1] != "K":
                    piecePositionScore = piecePositionScores[piece][row][col]
                if piece[0] == "w":
                    score += pieceScores[piece[1]] + piecePositionScore
                if piece[0] == "b":
                    score -= pieceScores[piece[1]] + piecePositionScore

