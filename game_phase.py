import typing as t

import chess
from chess import  SQUARES, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, WHITE, BLACK
from chess import (A1, B1, C1, D1, E1, F1, G1, H1, A2, B2, C2, D2, E2, F2, G2,
                   H2, A3, B3, C3, D3, E3, F3, G3, H3, A4, B4, C4, D4, E4, F4, G4, H4, A5,
                   B5, C5, D5, E5, F5, G5, H5, A6, B6, C6, D6, E6, F6, G6, H6, A7, B7, C7,
                   D7, E7, F7, G7, H7, A8, B8, C8, D8, E8, F8, G8, H8)

WHITE_BACKRANK = [A1, B1, C1, D1, E1, F1, G1, H1]
BLACK_BACKRANK = [A8, B8, C8, D8, E8, F8, G8, H8]

SQUARES_ARRAY = [[A1, A2, A3, A4, A5, A6, A7, A8,],
                 [B1, B2, B3, B4, B5, B6, B7, B8,],
                 [C1, C2, C3, C4, C5, C6, C7, C8,],
                 [D1, D2, D3, D4, D5, D6, D7, D8,],
                 [E1, E2, E3, E4, E5, E6, E7, E8,],
                 [F1, F2, F3, F4, F5, F6, F7, F8,],
                 [G1, G2, G3, G4, G5, G6, G7, G8,],
                 [H1, H2, H3, H4, H5, H6, H7, H8,],]





def get_game_phases(boards: t.List[chess.Board]) -> (t.Optional[int], t.Optional[int]):
    """
    Given a list of boards, return a tuple (i, j) where i is the the index of
    the first midgame board (or None if the game ended before midgame) and j is
    the index of the first endgame board (or None if the game ended before
    endgame)

    Algorithim shamelessly stolen from lichess. See
    https://github.com/ornicar/scalachess/blob/2d4aa7e2db77ce7dff353ccbc61ed4529669f5f7/src/main/scala/Divider.scala
    """
    mid_game_index = next((i for (i, board) in enumerate(boards)
                           if majors_and_minors(board) <= 10 or
                              backrank_is_sparse(board) or
                              mixedness(board) > 150), None)

    end_game_index = (
        mid_game_index and
        next((i for (i, board) in enumerate(boards)
              if i > mid_game_index and
                 majors_and_minors(board) <= 6), None)
    )

    return (mid_game_index, end_game_index)


def majors_and_minors(board: chess.Board) -> int:
    pieces = (board.piece_at(square) for square in SQUARES) # either a piece or None
    majors_and_minors = (piece for piece in pieces
                         if piece is not None and
                         piece.piece_type in  [KNIGHT, BISHOP, ROOK, QUEEN])
    return len(list(majors_and_minors))


def backrank_is_sparse(board: chess.Board) -> bool:
    white_backrank_pieces = (board.piece_at(square) for square in WHITE_BACKRANK)

    white_backrank_count = len([piece for piece in white_backrank_pieces
                                if piece is not None and piece.color == WHITE])

    black_backrank_pieces = (board.piece_at(square) for square in BLACK_BACKRANK)

    black_backrank_count = len([piece for piece in black_backrank_pieces
                                if piece is not None and piece.color == BLACK])

    return white_backrank_count < 4 or black_backrank_count < 4


def mixedness(board: chess.Board) -> int:
    regions = [[(x + dx, y + dy) for dx in [0, 1] for dy in [0, 1] ]
               for x in range(7) for y in range(7)]
    total = 0
    for region in regions:
        pieces  = [board.piece_at(SQUARES_ARRAY[x][y]) for x,y in region]
        nwhites = sum([1 for piece in pieces if piece is not None and piece.color == WHITE])
        nblacks = sum([1 for piece in pieces if piece is not None and piece.color == BLACK])
        ycoord  = region[0][1]
        total   += score(nwhites, nblacks, ycoord)
    return total


def score(nwhite: int, nblack: int, ycoord: int) -> int:
    """
    I have no idea what madman concocted this algorithm. Stole it (and the rest
    of this file) from here.
    https://github.com/ornicar/scalachess/blob/2d4aa7e2db77ce7dff353ccbc61ed4529669f5f7/src/main/scala/Divider.scala

    score "scores" each 2x2 tile of the chessboard. The total "mixedness" is
    the sum of the score of all 2x2 tiles. Score is high if you have a 2x2 tile
    with a lot of black and white pieces, or if you have black pieces on the
    white side of the board or white pieces on the black side of the board.

    What I don't understand is that the score is weirdly asymetric. For example
    a tile with one white and one black has a higher score if it's on the black
    side than the white side. Also
        score(2, 1, y) for y <- 0 to 7
    is not the same as
        score(1, 2, y) for y <- 7 to 0
    """
    tup = (nwhite, nblack)
    y = ycoord + 1

    if tup == (0, 0) : return 0

    if tup == (1, 0) : return 1 + (8 - y)
    if tup == (2, 0) : return 2 + (y - 2) if (y > 2) else 0
    if tup == (3, 0) : return 3 + (y - 1) if (y > 1) else 0
    if tup == (4, 0) : return 3 + (y - 1) if (y > 1) else 0 # group of 4 on the homerow = 0

    if tup == (0, 1) : return 1 + y
    if tup == (1, 1) : return 5 + abs(3 - y)
    if tup == (2, 1) : return 4 + y
    if tup == (3, 1) : return 5 + y

    if tup == (0, 2) : return 2 + (6 - y) if (y < 6) else 0
    if tup == (1, 2) : return 4 + (6 - y)
    if tup == (2, 2) : return 7

    if tup == (0, 3) : return 3 + (7 - y) if (y < 7) else 0
    if tup == (1, 3) : return 5 + (6 - y)

    if tup == (0, 4) : return 3 + (7 - y) if (y < 7) else 0

    return 0

