import sys
import numpy as np

sys.path.append('..')
from Game import Game
from .Connect4Logic import Board
from .Connect4Constants import Connect4Constants as constants
import pygame

class Connect4Game(Game):
    """
    Connect4 Game class implementing the alpha-zero-general Game interface.
    """

    def __init__(self, height=None, width=None, win_length=None, np_pieces=None):
        Game.__init__(self)
        self._base_board = Board(height, width, win_length, np_pieces)
        self.initPygame()
    def getInitBoard(self):
        return self._base_board.np_pieces

    def getBoardSize(self):
        return (self._base_board.height, self._base_board.width)

    def getActionSize(self):
        return self._base_board.width

    def getNextState(self, board, player, action):
        """Returns a copy of the board with updated move, original board is unmodified."""
        b = self._base_board.with_np_pieces(np_pieces=np.copy(board))
        b.add_stone(action, player)
        return b.np_pieces, -player

    def getValidMoves(self, board, player):
        "Any zero value in top row in a valid move"
        return self._base_board.with_np_pieces(np_pieces=board).get_valid_moves()

    def getGameEnded(self, board, player):
        b = self._base_board.with_np_pieces(np_pieces=board)
        winstate = b.get_win_state()
        if winstate.is_ended:
            if winstate.winner is None:
                # draw has very little value.
                return 1e-4
            elif winstate.winner == player:
                return +1
            elif winstate.winner == -player:
                return -1
            else:
                raise ValueError('Unexpected winstate found: ', winstate)
        else:
            # 0 used to represent unfinished game.
            return 0

    def getCanonicalForm(self, board, player):
        # Flip player from 1 to -1
        return board * player

    def getSymmetries(self, board, pi):
        """Board is left/right board symmetric"""
        return [(board, pi), (board[:, ::-1], pi[::-1])]

    def stringRepresentation(self, board):
        return str(self._base_board.with_np_pieces(np_pieces=board))

    def initPygame(self):
        # define constants
        self.SQUARE_SIZE = constants.SQUARE_SIZE # pixels
        shape = self.getBoardSize()
        self.row = shape[0]
        self.column = shape[1]
        self.width_px = self.column * self.SQUARE_SIZE
        self.height_px = (self.row+1) * self.SQUARE_SIZE
        size = (self.width_px,self.height_px)

        self.RADIUS = constants.RADIUS

        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.font.init()
        self.myfont = pygame.font.SysFont('monospace', 50)
    

    def display_pygame(self,board):
            board = np.flip(board, 0)
            sqsz = self.SQUARE_SIZE
            for c in range(self.column):
                for r in range(self.row):
                    pygame.draw.rect(self.screen, constants.BLUE, (c*sqsz, r*sqsz+sqsz, sqsz, sqsz))
                    pygame.draw.circle(self.screen, constants.BLACK, (int(c*sqsz+sqsz/2), int(r*sqsz+sqsz+sqsz/2)), self.RADIUS)

            for c in range(self.column):
                for r in range(self.row):
                    if board[r][c] == constants.P1_PIECE:
                        pygame.draw.circle(self.screen, constants.RED, (int(c*sqsz+sqsz/2), self.height_px-int(r*sqsz+sqsz/2)), self.RADIUS)
                    elif board[r][c] == constants.P2_PIECE: 
                        pygame.draw.circle(self.screen, constants.YELLOW, (int(c*sqsz+sqsz/2), self.height_px-int(r*sqsz+sqsz/2)), self.RADIUS)
            pygame.display.update()


def display(board):
    print(" -----------------------")
    print(' '.join(map(str, range(len(board[0])))))
    print(board)
    print(" -----------------------")
