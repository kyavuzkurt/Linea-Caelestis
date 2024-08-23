import os
import pygame as p
import chess
import chess.engine
from multiprocessing import Process, Queue
from search import Search


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ["wP", "wB", "wQ", "wK", "wN", "wR", "bP", "bB", "bQ", "bK", "bN", "bR"]
    base_path = os.path.join(os.path.dirname(__file__), "images")
    for piece in pieces:
        img_path = os.path.join(base_path, piece + ".png")
        img = p.transform.scale(p.image.load(img_path), (SQ_SIZE, SQ_SIZE))
        IMAGES[piece] = img
    return IMAGES

def drawBoard(screen):
    colors = [p.Color("brown"), p.Color("white")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board.piece_at(chess.square(c, r))
            if piece:
                piece_str = piece.symbol()
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_key = piece_color + piece_str.upper()
                screen.blit(IMAGES[piece_key], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawGameState(screen, board, validMoves, sqSelected):
    drawBoard(screen)
    highlighting(screen, board, validMoves, sqSelected)
    drawPieces(screen, board)

def highlighting(screen, board, validMoves, sqSelected):
    if sqSelected:
        r, c = sqSelected
        square = chess.square(c, r)
        piece = board.piece_at(square)
        if piece and piece.color == (chess.WHITE if board.turn else chess.BLACK):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.from_square == square:
                    to_r, to_c = chess.square_rank(move.to_square), chess.square_file(move.to_square)
                    screen.blit(s, (to_c * SQ_SIZE, to_r * SQ_SIZE))

def drawText(screen, text):
    font = p.font.SysFont("Calibri", 32, True, False)
    textObject = font.render(text, 0, p.Color('black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    loadImages()
    board = chess.Board()
    validMoves = list(board.legal_moves)
    isWhite = True # Change to true if you want to play as black
    moveMade = False
    gameOver = False
    animate = False
    running = True
    engineThinking = False
    moveFinderProcess = None
    sqSelected = ()
    playerClicks = []

    search = Search(board=board, depth=10, isWhite=isWhite)  # Initialize the Search class

    while running:
        humanTurn = (board.turn and not isWhite) or (not board.turn and isWhite)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = chess.Move.from_uci(chess.square_name(chess.square(playerClicks[0][1], playerClicks[0][0])) +
                                                   chess.square_name(chess.square(playerClicks[1][1], playerClicks[1][0])))
                        if move in validMoves:
                            board.push(move)
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
                            print("Invalid Move")

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if board.move_stack:
                        board.pop()
                        moveMade = True
                        print("Move undone")
                if e.key == p.K_r:
                    board.reset()
                    validMoves = list(board.legal_moves)
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False

        if not gameOver and not humanTurn:
            engineThinking = True
            best_move = search.BestMove()  # Get the best move from the engine
            if best_move:
                board.push(best_move)
                moveMade = True
            engineThinking = False

        if moveMade:
            validMoves = list(board.legal_moves)
            moveMade = False
        drawGameState(screen, board, validMoves, sqSelected)
        if board.is_checkmate():
            gameOver = True
            if board.turn:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif board.is_stalemate():
            gameOver = True
            drawText(screen, 'Draw')
        clock.tick(MAX_FPS)
        p.display.flip()