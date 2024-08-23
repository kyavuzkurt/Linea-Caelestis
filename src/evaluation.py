import chess

class Evaluation:
    PAWN_TABLE = [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, -20, -20, 10, 10, 5,
        5, -5, -10, 0, 0, -10, -5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, 5, 10, 25, 25, 10, 5, 5,
        10, 10, 20, 30, 30, 20, 10, 10,
        50, 50, 50, 50, 50, 50, 50, 50,
        0, 0, 0, 0, 0, 0, 0, 0
    ]

    KNIGHT_TABLE = [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ]

    BISHOP_TABLE = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ]

    ROOK_TABLE = [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0
    ]

    QUEEN_TABLE = [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ]

    KING_TABLE_MID = [
        20, 30, 10, 0, 0, 10, 30, 20,
        20, 20, 0, 0, 0, 0, 20, 20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30
    ]

    KING_TABLE_END = [
        -50, -40, -30, -20, -20, -30, -40, -50,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -30, 0, 0, 0, 0, -30, -30,
        -50, -30, -30, -30, -30, -30, -30, -50
    ]

    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    def __init__(self, board):
        self.board = board

    def evaluate_board(self):
        if self.board.is_checkmate():
            if self.board.turn:
                return -float('inf')  # Black wins
            else:
                return float('inf')  # White wins
        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0  # Draw

        score = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_value = self.PIECE_VALUES[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += piece_value
                    score += self.get_piece_square_value(piece, square)
                else:
                    score -= piece_value
                    score -= self.get_piece_square_value(piece, square)

        return score

    def get_piece_square_value(self, piece, square):
        if piece.piece_type == chess.PAWN:
            return self.PAWN_TABLE[square] if piece.color == chess.WHITE else self.PAWN_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.KNIGHT:
            return self.KNIGHT_TABLE[square] if piece.color == chess.WHITE else self.KNIGHT_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.BISHOP:
            return self.BISHOP_TABLE[square] if piece.color == chess.WHITE else self.BISHOP_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.ROOK:
            return self.ROOK_TABLE[square] if piece.color == chess.WHITE else self.ROOK_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.QUEEN:
            return self.QUEEN_TABLE[square] if piece.color == chess.WHITE else self.QUEEN_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.KING:
            if self.is_endgame():
                return self.KING_TABLE_END[square] if piece.color == chess.WHITE else self.KING_TABLE_END[chess.square_mirror(square)]
            else:
                return self.KING_TABLE_MID[square] if piece.color == chess.WHITE else self.KING_TABLE_MID[chess.square_mirror(square)]
        return 0

    def is_endgame(self):
        return chess.popcount(self.board.occupied_co[chess.WHITE]) + chess.popcount(self.board.occupied_co[chess.BLACK]) <= 12