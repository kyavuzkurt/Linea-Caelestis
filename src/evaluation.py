import chess
from collections import defaultdict
from functools import lru_cache

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
        self.mirrored_tables = self._precompute_mirrored_tables()
        self.WEIGHTS = {
            'material': 1.0,
            'pawn_structure': 1.0,
            'piece_activity': 1.0,
            'king_safety': 1.0,
            'control_key_squares': 1.0
        }

    def _precompute_mirrored_tables(self):
        mirrored = {}
        for piece_type in ['PAWN', 'KNIGHT', 'BISHOP', 'ROOK', 'QUEEN', 'KING_MID', 'KING_END']:
            table = getattr(self, f"{piece_type}_TABLE")
            mirrored[piece_type] = [table[chess.square_mirror(sq)] for sq in range(64)]
        return mirrored

    def evaluate_board(self):

        if self.board.is_checkmate():
            return -float('inf') if self.board.turn else float('inf')
        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        score = 0
        score += self.WEIGHTS['material'] * self.evaluate_material()
        score += self.WEIGHTS['pawn_structure'] * self.evaluate_pawn_structure()
        score += self.WEIGHTS['piece_activity'] * self.evaluate_piece_activity()
        score += self.WEIGHTS['king_safety'] * self.evaluate_king_safety()
        score += self.WEIGHTS['control_key_squares'] * self.evaluate_control_of_key_squares()

        return score

    def evaluate_material(self):
        material_score = 0
        for piece_type in self.PIECE_VALUES:
            white_pieces = self.board.pieces(piece_type, chess.WHITE)
            black_pieces = self.board.pieces(piece_type, chess.BLACK)
            material_score += len(white_pieces) * self.PIECE_VALUES[piece_type]
            material_score -= len(black_pieces) * self.PIECE_VALUES[piece_type]
        return material_score

    @lru_cache(maxsize=1024)
    def _count_isolated_pawns(self, pawn_files):
        isolated = 0
        for file in pawn_files:
            if (file == 0 or (file - 1) not in pawn_files) and \
               (file == 7 or (file + 1) not in pawn_files):
                isolated += 1
        return isolated

    def evaluate_pawn_structure(self):
        pawn_score = 0
        white_pawns = tuple(sorted([chess.square_file(p) for p in self.board.pieces(chess.PAWN, chess.WHITE)]))
        black_pawns = tuple(sorted([chess.square_file(p) for p in self.board.pieces(chess.PAWN, chess.BLACK)]))

        pawn_score += self._count_isolated_pawns(white_pawns) * -10
        pawn_score += self._count_doubled_pawns(white_pawns) * -10
        pawn_score += self._count_passed_pawns(white_pawns, chess.WHITE) * 50

        pawn_score -= self._count_isolated_pawns(black_pawns) * -10
        pawn_score -= self._count_doubled_pawns(black_pawns) * -10
        pawn_score -= self._count_passed_pawns(black_pawns, chess.BLACK) * 50

        return pawn_score

    def _count_doubled_pawns(self, pawns):
        counts = defaultdict(int)
        for pawn in pawns:
            counts[chess.square_file(pawn)] += 1
        doubled = sum(1 for count in counts.values() if count > 1)
        return doubled

    def _count_passed_pawns(self, pawns, color):
        passed = 0
        for pawn in pawns:
            file = chess.square_file(pawn)
            rank = chess.square_rank(pawn)
            if color == chess.WHITE:
                ahead_squares = [chess.square(file, r) for r in range(rank + 1, 8)]
            else:
                ahead_squares = [chess.square(file, r) for r in range(0, rank)]
            enemy_pawns = self.board.pieces(chess.PAWN, not color)
            blocked = any(p in ahead_squares for p in enemy_pawns)
            if not blocked:
                passed += 1
        return passed

    def evaluate_piece_activity(self):
        activity_score = 0
        activity_score += self._mobility_score(chess.WHITE)
        activity_score -= self._mobility_score(chess.BLACK)
        activity_score += self._central_control_score(chess.WHITE)
        activity_score -= self._central_control_score(chess.BLACK)
        activity_score += self._rook_open_file_bonus(chess.WHITE)
        activity_score -= self._rook_open_file_bonus(chess.BLACK)
        return activity_score

    def _mobility_score(self, color):
        return len(list(self.board.legal_moves)) if self.board.turn == color else 0

    def _central_control_score(self, color):
        central_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        score = 0
        for sq in central_squares:
            attackers = self.board.attackers(color, sq)
            score += len(attackers) * 0.3  
        return score

    def _rook_open_file_bonus(self, color):
        bonus = 0
        rooks = self.board.pieces(chess.ROOK, color)
        for rook in rooks:
            file = chess.square_file(rook)
            file_squares = chess.BB_FILE_A << file
            pawn_files = self.board.pieces(chess.PAWN, color) & (chess.BB_FILE_A << file)
            enemy_pawns = self.board.pieces(chess.PAWN, not color) & (chess.BB_FILE_A << file)
            if not enemy_pawns:
                bonus += 0.5  # Open file
            elif len(enemy_pawns) == 1:
                bonus += 0.3  # Semi-open file
        return bonus

    def evaluate_king_safety(self):
        king_safety_score = 0
        for color in [chess.WHITE, chess.BLACK]:
            king_square = self.board.king(color)
            if king_square is None:
                continue  # King is checkmated
            shield_pawns = self._count_pawn_shield(king_square, color)
            enemy_attacks = self._count_enemy_attacks(king_square, color)
            king_safety_score += (shield_pawns * 2 - enemy_attacks * 5) if color == chess.WHITE else (-shield_pawns * 2 + enemy_attacks * 5)
        return king_safety_score

    def _count_pawn_shield(self, king_square, color):
        shield_pawns = 0
        king_file = chess.square_file(king_square)
        if color == chess.WHITE:
            pawn_ranks = [chess.square_rank(king_square) - 1]
        else:
            pawn_ranks = [chess.square_rank(king_square) + 1]
        for fr in pawn_ranks:
            for ff in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
                sq = chess.square(ff, fr)
                if self.board.piece_at(sq) == chess.Piece(chess.PAWN, color):
                    shield_pawns += 1
        return shield_pawns

    def _count_enemy_attacks(self, king_square, color):
        enemy_attacks = self.board.attackers(not color, king_square)
        return len(enemy_attacks)

    def evaluate_control_of_key_squares(self):
        control_score = 0
        central_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        for sq in central_squares:
            attackers_white = self.board.attackers(chess.WHITE, sq)
            attackers_black = self.board.attackers(chess.BLACK, sq)
            control_score += len(attackers_white) * 0.5
            control_score -= len(attackers_black) * 0.5
        return control_score

    def get_piece_square_value(self, piece, square):
        table_name = ''
        if piece.piece_type == chess.PAWN:
            table_name = 'PAWN'
        elif piece.piece_type == chess.KNIGHT:
            table_name = 'KNIGHT'
        elif piece.piece_type == chess.BISHOP:
            table_name = 'BISHOP'
        elif piece.piece_type == chess.ROOK:
            table_name = 'ROOK'
        elif piece.piece_type == chess.QUEEN:
            table_name = 'QUEEN'
        elif piece.piece_type == chess.KING:
            table_name = 'KING_END' if self.is_endgame() else 'KING_MID'
        else:
            return 0

        if piece.color == chess.WHITE:
            return getattr(self, f"{table_name}_TABLE")[square]
        else:
            return self.mirrored_tables[f"{table_name}"]

    def is_endgame(self):
        total_material = sum(self.PIECE_VALUES[p] * len(self.board.pieces(p, chess.WHITE) | self.board.pieces(p, chess.BLACK))
                             for p in self.PIECE_VALUES)
        return total_material < 1500  # Threshold can be adjusted