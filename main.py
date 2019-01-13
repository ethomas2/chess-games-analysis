from itertools import *
import typing as t

import chess.pgn
import chess
import chess.uci
import chess.svg

from game_phase import get_game_phases


class SilentGameCreator(chess.pgn.GameCreator):
    """
    By default chess.pgn.read_game prints out every parsing error to stdout.
    This is really annoying and noisy. Pass in SilentGameCreator to silence
    these errors.
    """
    def handle_error(self, err):
        if isinstance(err, ValueError) and str(err).startswith('unsupported variant'):
            pass

def all_games() -> t.Iterator[chess.pgn.Game]:
    pgn = open('data/lichess_evanrthomas_2019-01-13.pgn')
    while True:
        try:
            # game = chess.pgn.read_game(pgn, Visitor=SilentGameCreator)
            game = chess.pgn.read_game(pgn, Visitor=SilentGameCreator)
            if game is None: break
            yield game
        except ValueError as e:
            pass

def evan_lost_game(game: chess.pgn.Game) -> bool:
    return (game.headers['White'] == 'evanrthomas' and game.headers['Result'] == '0-1' or
            game.headers['Black'] == 'evanrthomas' and game.headers['Result'] == '1-0' )


def get_boards(game: chess.pgn.Game) -> t.List[chess.Board]:
    boards = []

    # some python magic bc I fucking can
    visit_board = lambda self, board: boards.append(board.copy())
    visitor_cls = type("AnonymousVisitor", (chess.pgn.BaseVisitor,),
                       {'visit_board': visit_board})
    game.accept(visitor_cls())
    return boards

engine = chess.uci.popen_engine('stockfish')
engine.uci()
engine.uciok.wait()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

def evaluate_game(game: chess.pgn.Game, total_seconds: int=60):
    boards = get_boards(game)
    movetime = min(5*1000, total_seconds*1000 // len(boards)) # spend 1 minute thinking about this board
    for board in boards:
        engine.position(board)
        engine.go(movetime=movetime)
        with info_handler:
            score = info_handler.info['score'][1]
            cp, mate = score.cp, score.mate
            yield board, (cp * (2*int(board.turn ) - 1))



standard_games = (game for game in all_games() if game.headers['Variant'] == 'Standard')
lost_games = (game for game in standard_games if evan_lost_game(game))
game1 = next(lost_games)
print(get_game_phases(get_boards(game1)), game1.headers["Site"])
