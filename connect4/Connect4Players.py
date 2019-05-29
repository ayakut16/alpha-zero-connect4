import numpy as np
import math
import random
import sys
import pygame
from .Connect4Constants import Connect4Constants as constants

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a] != 1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanConnect4Player():
    def __init__(self, game):
        self.game = game
        self.color = constants.RED
    def play(self, board):
        valid_moves = self.game.getValidMoves(board, 1)
        print('\nMoves:', [i for (i, valid) in enumerate(valid_moves) if valid])
        flag = False
        if board.sum() == -1:
            self.color = constants.YELLOW
        elif board.sum() == 0:
            self.color = constants.RED
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(self.game.screen, constants.BLACK, (0,0,self.game.width_px,constants.SQUARE_SIZE))
                    posx = event.pos[0]
                    pygame.draw.circle(self.game.screen, self.color, (posx,int(constants.SQUARE_SIZE/2)), constants.RADIUS)
                    pygame.display.update()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(self.game.screen, constants.BLACK, (0,0, self.game.width_px, constants.SQUARE_SIZE))
                    posx = event.pos[0]
                    move = int( math.floor( posx / constants.SQUARE_SIZE ) )
                    if valid_moves[move]:
                        flag = True
                        break
            if flag: break
        return move


class OneStepLookaheadConnect4Player():
    """Simple player who always takes a win if presented, or blocks a loss if obvious, otherwise is random."""

    def __init__(self, game, verbose=True):
        self.game = game
        self.player_num = 1
        self.verbose = verbose

    def play(self, board):
        valid_moves = self.game.getValidMoves(board, self.player_num)
        win_move_set = set()
        fallback_move_set = set()
        stop_loss_move_set = set()
        for move, valid in enumerate(valid_moves):
            if not valid:
                continue
            if self.player_num == self.game.getGameEnded(*self.game.getNextState(board, self.player_num, move)):
                win_move_set.add(move)
            if -self.player_num == self.game.getGameEnded(*self.game.getNextState(board, -self.player_num, move)):
                stop_loss_move_set.add(move)
            else:
                fallback_move_set.add(move)

        if len(win_move_set) > 0:
            ret_move = np.random.choice(list(win_move_set))
            if self.verbose:
                print('Playing winning action %s from %s' %
                      (ret_move, win_move_set))
        elif len(stop_loss_move_set) > 0:
            ret_move = np.random.choice(list(stop_loss_move_set))
            if self.verbose:
                print('Playing loss stopping action %s from %s' %
                      (ret_move, stop_loss_move_set))
        elif len(fallback_move_set) > 0:
            ret_move = np.random.choice(list(fallback_move_set))
            if self.verbose:
                print('Playing random action %s from %s' %
                      (ret_move, fallback_move_set))
        else:
            raise Exception('No valid moves remaining: %s' %
                            self.game.stringRepresentation(board))

        return ret_move


class MinimaxConnect4Player():
    def __init__(self, game, verbose=True):
        self.game = game
        self.player_num = 1
        self.verbose = verbose

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = -piece

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 4

        return score

    def score_position(self, board, piece):
        score = 0
        board_height, board_width = self.game.getBoardSize()
        # Score center column
        center_array = [int(i) for i in list(board[:, board_width//2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(board_height):
            row_array = [int(i) for i in list(board[r, :])]
            for c in range(board_width-3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(board_width):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(board_height-3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(board_height-3):
            for c in range(board_width-3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        for r in range(board_height-3):
            for c in range(board_width-3):
                window = [board[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_moves = self.game.getValidMoves(
            board, self.player_num if maximizingPlayer else -self.player_num)
        valid_moves = [i for (i, valid)
                       in enumerate(valid_moves) if valid]
        gameEnded = self.game.getGameEnded(board, self.player_num)

        if depth == 0 or gameEnded:
            if gameEnded:
                if gameEnded == 1 or gameEnded == -1:
                    return (None, gameEnded * 100000000000000)
                else:  # Game is over, no more valid moves
                    return (None, 0)
            else:  # Depth is zero
                return (None, self.score_position(board, self.player_num))

        if maximizingPlayer:
            value = -math.inf
            column = np.random.choice(valid_moves)
            for col in valid_moves:
                next_board, _ = self.game.getNextState(
                    board, self.player_num, col)
                _, new_score = self.minimax(
                    next_board, depth-1, alpha, beta, False)
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else:  # Minimizing player
            value = math.inf
            column = np.random.choice(valid_moves)
            for col in valid_moves:
                next_board, _ = self.game.getNextState(
                    board, -self.player_num, col)
                _, new_score = self.minimax(
                    next_board, depth-1, alpha, beta, True)
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def play(self, board):
        s, t = self.minimax(board, 4, -math.inf, math.inf, True)
        return s