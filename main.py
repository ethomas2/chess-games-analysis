from itertools import *
import time
import typing as t
import json
import sys

import chess.pgn
import chess
import chess.uci
from chess import BLACK, WHITE

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
    pgn = open('games.pgn')
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

def evaluate_game(game: chess.pgn.Game, total_seconds: int=60) -> t.Iterator[t.Tuple[chess.Board, float]]:
    boards = get_boards(game)
    movetime = min(5*1000, total_seconds*1000 // len(boards)) # spend 1 minute thinking about this board
    sign = lambda x: 1 if x > 0 else (0 if x == 0 else -1)
    for board in boards:
        engine.position(board)
        engine.go(movetime=movetime)
        with info_handler:
            score = info_handler.info['score'][1]
            cp, mate = score.cp, score.mate
            if mate is not None: print('mate', mate)
            score = float(cp) / 1000 if cp is not None else sign(mate)*float('+inf')

            # Evaluation is given for whoever's turn it is. If it's black's turn, multiply by -1
            yield board, (score * (-1 if board.turn == BLACK else 1))

def lost_by_endgame(game: chess.pgn.Game) -> bool:
    if not evan_lost_game(game):
        return False
    boards_with_evaluations = list(evaluate_game(game, 60))
    _, end_game_index = get_game_phases(get_boards(game))
    if end_game_index is None: return False

    board_before_endgame, evaluation = boards_with_evaluations[end_game_index - 1]
    losing_before_endgame  = (evaluation < -0.3 if board_before_endgame.turn == WHITE
                              else evaluation > 0.3)
    if not losing_before_endgame: return True

with open('cache', 'r') as f: # opening in write mode just so we can create if it doesn't exist
    cache = [json.loads(line) for line in f.read().splitlines() if line != '']

already_evaluated =  set([elm['Site'] for elm in cache])
print('Cache loaded \n{}'.format('\n'.join('\t' + site for site in already_evaluated)))

standard_games = (game for game in all_games() if game.headers['Variant'] == 'Standard')
lost_games = (game for game in standard_games if evan_lost_game(game))
with open('cache', 'a') as f:
    for game in lost_games:
        if game.headers['Site'] in already_evaluated:
            print('skipping', game.headers['Site'])
            continue
        print('Evaluating game ', game.headers['Site'], end='\t')
        sys.stdout.flush()
        did_lose_by_endgame = lost_by_endgame(game)
        if did_lose_by_endgame: print('Lost by endgame')
        else:                   print('Did not lose by endgame')
        f.write(json.dumps({
            'Site': game.headers['Site'],
            'Result': 'Lost',
            'Reason': 'Endgame' if did_lose_by_endgame else 'Other',
        }))
        f.write('\n')
        f.flush()
