import random

def randomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def bestMove():
    return