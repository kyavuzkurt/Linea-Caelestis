import chess

def evaluate_pawn_structure(board):
    score = 0
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    for file in range(8):
        white_pawns_in_file = sum(1 for sq in white_pawns if chess.square_file(sq) == file)
        black_pawns_in_file = sum(1 for sq in black_pawns if chess.square_file(sq) == file)
        if white_pawns_in_file > 1:
            score -= 10 * (white_pawns_in_file - 1)
        if black_pawns_in_file > 1:
            score += 10 * (black_pawns_in_file - 1)

    for pawn in white_pawns:
        file = chess.square_file(pawn)
        if (file == 0 or not any(chess.square_file(p) == file - 1 for p in white_pawns)) and \
           (file == 7 or not any(chess.square_file(p) == file + 1 for p in white_pawns)):
            score -= 20
    for pawn in black_pawns:
        file = chess.square_file(pawn)
        if (file == 0 or not any(chess.square_file(p) == file - 1 for p in black_pawns)) and \
           (file == 7 or not any(chess.square_file(p) == file + 1 for p in black_pawns)):
            score += 20

    for pawn in white_pawns:
        file = chess.square_file(pawn)
        rank = chess.square_rank(pawn)
        if all(chess.square_rank(p) < rank for p in black_pawns if abs(chess.square_file(p) - file) <= 1):
            score += 30 + 5 * rank
    for pawn in black_pawns:
        file = chess.square_file(pawn)
        rank = chess.square_rank(pawn)
        if all(chess.square_rank(p) > rank for p in white_pawns if abs(chess.square_file(p) - file) <= 1):
            score -= 30 + 5 * (7 - rank)

    return score


def evaluate_bishops(board):
    score = 0
    white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
    black_bishops = board.pieces(chess.BISHOP, chess.BLACK)

    # Evaluate bishop pair
    if len(white_bishops) == 2:
        score += 30
    if len(black_bishops) == 2:
        score -= 30

    # Evaluate bad bishops
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    for bishop in white_bishops:
        bishop_color = chess.square_rank(bishop) % 2 == chess.square_file(bishop) % 2
        blocked_pawns = sum(1 for pawn in white_pawns if 
                            chess.square_rank(pawn) > chess.square_rank(bishop) and
                            (chess.square_rank(pawn) % 2 == chess.square_file(pawn) % 2) == bishop_color)
        score -= 5 * blocked_pawns

    for bishop in black_bishops:
        bishop_color = chess.square_rank(bishop) % 2 == chess.square_file(bishop) % 2
        blocked_pawns = sum(1 for pawn in black_pawns if 
                            chess.square_rank(pawn) < chess.square_rank(bishop) and
                            (chess.square_rank(pawn) % 2 == chess.square_file(pawn) % 2) == bishop_color)
        score += 5 * blocked_pawns

    return score


def evaluate_king_safety(board):
    score = 0
    
    def king_zone(king_square):
        file, rank = chess.square_file(king_square), chess.square_rank(king_square)
        return [chess.square(f, r) for f in range(max(0, file-1), min(7, file+1)+1)
                for r in range(max(0, rank-1), min(7, rank+1)+1)]
    
    def pawn_shield_score(king_square, pawns, multiplier):
        shield_score = 0
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        front_squares = [chess.square(f, king_rank + multiplier) for f in range(max(0, king_file-1), min(7, king_file+1)+1)]
        for square in front_squares:
            if square in pawns:
                shield_score += 10
            elif chess.square(chess.square_file(square), king_rank + 2*multiplier) in pawns:
                shield_score += 5
        return shield_score * multiplier
    
    def open_files_near_king(king_square, pawns):
        king_file = chess.square_file(king_square)
        files_to_check = [f for f in range(max(0, king_file-1), min(7, king_file+1)+1)]
        return sum(1 for f in files_to_check if not any(chess.square_file(p) == f for p in pawns))
    
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)
    
    # Evaluate pawn shield for both kings
    score += pawn_shield_score(white_king, white_pawns, 1)
    score -= pawn_shield_score(black_king, black_pawns, -1)
    
    # Penalize open files near kings
    score -= 15 * open_files_near_king(white_king, white_pawns)
    score += 15 * open_files_near_king(black_king, black_pawns)
    
    # Penalize kings in the center during early/mid-game
    piece_count = len(board.piece_map())
    if piece_count > 20:  # Adjust this threshold as needed
        center_distance_white = min(abs(3.5 - chess.square_file(white_king)), abs(3.5 - chess.square_rank(white_king)))
        center_distance_black = min(abs(3.5 - chess.square_file(black_king)), abs(3.5 - chess.square_rank(black_king)))
        score += 5 * center_distance_white
        score -= 5 * center_distance_black
    
    return score


def evaluate_piece_mobility(board):
    score = 0
    
 
    mobility_weights = {
        chess.PAWN: 0.1,
        chess.KNIGHT: 0.4,
        chess.BISHOP: 0.4,
        chess.ROOK: 0.5,
        chess.QUEEN: 0.8
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.KING:
            moves = len(list(board.legal_moves))
            
            temp_board = board.copy()
            temp_board.push(chess.Move.null())
            piece_moves = sum(1 for move in temp_board.legal_moves if move.from_square == square)
            mobility_score = piece_moves * mobility_weights[piece.piece_type]
            mobility_score = piece_moves * mobility_weights[piece.piece_type]
            
            if piece.color == chess.WHITE:
                score += mobility_score
            else:
                score -= mobility_score

    return score