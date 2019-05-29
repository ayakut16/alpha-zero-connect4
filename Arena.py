import numpy as np
from pytorch_classification.utils import Bar, AverageMeter
import time
import pygame

BLUE = (0,0,255)
RED = (220,20,60)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
P1_PIECE = 1
P2_PIECE = -1
class Arena():
    """
    An Arena class where any 2 agents can be pit against each other.
    """
    def __init__(self, player1, player2, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        #self.display = display
        self.display = self.display_pygame
        self.initPygame()
    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        players = [self.player2, None, self.player1]
        curPlayer = 1
        board = self.game.getInitBoard()

        it = 0
        while self.game.getGameEnded(board, curPlayer)==0:
            it+=1
            if verbose:
                assert(self.display)
                print("Turn ", str(it), "Player ", str(curPlayer))
                self.display(board)
            action = players[curPlayer+1](self.game.getCanonicalForm(board, curPlayer))

            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer),1)

            if valids[action]==0:
                print(action)
                assert valids[action] >0
            board, curPlayer = self.game.getNextState(board, curPlayer, action)
        if verbose:
            assert(self.display)
            print("Game over: Turn ", str(it), "Result ", str(self.game.getGameEnded(board, 1)))
            self.display(board)
        return self.game.getGameEnded(board, 1)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        eps_time = AverageMeter()
        bar = Bar('Arena.playGames', max=num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(num/2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult==1:
                oneWon+=1
            elif gameResult==-1:
                twoWon+=1
            else:
                draws+=1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps, maxeps=maxeps, et=eps_time.avg,
                                                                                                       total=bar.elapsed_td, eta=bar.eta_td)
            bar.next()

        self.player1, self.player2 = self.player2, self.player1
        
        for _ in range(num):
            gameResult = self.playGame(verbose=verbose)
            if gameResult==-1:
                oneWon+=1                
            elif gameResult==1:
                twoWon+=1
            else:
                draws+=1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix  = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps, maxeps=maxeps, et=eps_time.avg,
                                                                                                       total=bar.elapsed_td, eta=bar.eta_td)
            bar.next()
            
        bar.finish()

        return oneWon, twoWon, draws
    def initPygame(self):
        # define constants 
        self.SQUARE_SIZE = 60 # pixels
        shape = self.game.getBoardSize()
        self.row = shape[0]
        self.column = shape[1]
        self.width_px = self.column * self.SQUARE_SIZE
        self.height_px = (self.row+1) * self.SQUARE_SIZE
        size = (self.width_px,self.height_px)

        self.RADIUS = int(self.SQUARE_SIZE*9/20)

        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.font.init()
        self.myfont = pygame.font.SysFont('monospace', 50)
    
    def display_pygame(self,board):
        board = np.flip(board, 0)
        sqsz = self.SQUARE_SIZE
        for c in range(self.column):
            for r in range(self.row):
                pygame.draw.rect(self.screen, BLUE, (c*sqsz, r*sqsz+sqsz, sqsz, sqsz))
                pygame.draw.circle(self.screen, BLACK, (int(c*sqsz+sqsz/2), int(r*sqsz+sqsz+sqsz/2)), self.RADIUS)

        for c in range(self.column):
            for r in range(self.row):
                if board[r][c] == P1_PIECE:
                    pygame.draw.circle(self.screen, RED, (int(c*sqsz+sqsz/2), self.height_px-int(r*sqsz+sqsz/2)), self.RADIUS)
                elif board[r][c] == P2_PIECE: 
                    pygame.draw.circle(self.screen, YELLOW, (int(c*sqsz+sqsz/2), self.height_px-int(r*sqsz+sqsz/2)), self.RADIUS)
        pygame.display.update()