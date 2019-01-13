import chess.pgn
import chess
import chess.uci
import chess.svg



class SilentGameCreator(chess.pgn.GameCreator):
    """
    By default chess.pgn.read_game prints out every parsing error to stdout.
    This is really annoying and noisy. Pass in SilentGameCreator to silence
    these errors.
    """
    def handle_error(self, err):
        if isinstance(err, ValueError) and str(err).startswith('unsupported variant'):
            pass

def all_games():
    pgn = open('data/lichess_evanrthomas_2019-01-13.pgn')
    while True:
        try:
            # game = chess.pgn.read_game(pgn, Visitor=SilentGameCreator)
            game = chess.pgn.read_game(pgn, Visitor=SilentGameCreator)
            if game is None: break
            yield game
        except ValueError as e:
            pass

def evan_lost_game(game):
    return (game.headers['White'] == 'evanrthomas' and game.headers['Result'] == '1-0' or
            game.headers['Black'] == 'evanrthomas' and game.headers['Result'] == '0-1' )


engine = chess.uci.popen_engine('stockfish')
engine.uci()
engine.uciok.wait()

def get_boards(game):
    boards = []
    class Visitor(chess.pgn.BaseVisitor):
        def __init__(self):
            self.lastboard = None

        def visit_board(self, board):
            boards.append(board.copy())
            return True

    game.accept(Visitor())
    return boards



standard_games = (game for game in all_games() if game.headers['Variant'] == 'Standard')
lost_games = (game for game in standard_games if evan_lost_game(game))
boards = get_boards(next(lost_games))
for board in boards:
    print(board)
    print()
