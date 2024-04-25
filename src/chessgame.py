import pygame as p
import chessengine, searchAndEvaluation
import sys
from multiprocessing import Process, Queue
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ["wP", "wB", "wQ", "wK", "wN", "wR", "bP", "bB", "bQ", "bK", "bN", "bR"]
    for piece in pieces:
        img = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        IMAGES[piece] = img
    return IMAGES
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("brown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlighting(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def highlighting(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.rowStart == r and move.colStart == c:
                    screen.blit(s, (SQ_SIZE * move.colEnd, SQ_SIZE * move.rowEnd))
def drawText(screen, text):
    font = p.font.SysFont("Calibri", 32, True, False)
    textObject = font.render(text, 0, p.Color('black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)

if __name__ == "__main__":
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    loadImages()
    gs = chessengine.ChessBoard()
    validMoves = gs.getValidMoves()
    whitePlayer = True
    blackPlayer = False
    moveMade = False
    gameOver = False
    animate = False
    running = True
    engineThinking = False
    moveFinderProcess = None
    sqSelected = ()
    playerClicks = []
    while running:
        humanTurn = (gs.whiteToMove and whitePlayer) or (not gs.whiteToMove and blackPlayer)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = chessengine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                print("White to move") if gs.whiteToMove else print("Black to move")

                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                            print("Invalid Move")

            elif e.type ==p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    print("Move undone")
                    if engineThinking:
                        moveFinderProcess.terminate()
                if e.key == p.K_r:
                    gs = chessengine.ChessBoard()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if engineThinking:
                        moveFinderProcess.terminate()
                        engineThinking = False


        if not gameOver and not humanTurn:
            if not engineThinking:
                engineThinking = True
                returnQueue = Queue()
                moveFinderProcess = Process(target=searchAndEvaluation, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()
            if not moveFinderProcess.is_alive():
                engineMove = returnQueue.get()
                if engineMove is None:
                    engineMove = searchAndEvaluation.randomMove(validMoves)
                gs.makeMove(engineMove)
                moveMade = True
                engineThinking = False

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen,gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Draw')
        clock.tick(MAX_FPS)
        p.display.flip()



