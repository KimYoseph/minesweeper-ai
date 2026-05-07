# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action

# supplementary libraries
import heapq


class MyAI( AI ):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        self._board = []
        for i in range(rowDimension): # (row by col filed with None)
            self._board.append([])
            for j in range(colDimension):
                self._board[i].append(None)

        self._rowDimension = rowDimension
        self._colDimension = colDimension

        self._total_mines = totalMines
        self._move_x = startX
        self._move_y = startY

        self._frontier = []

        ########################################################################
        #							YOUR CODE ENDS							   #
        ########################################################################

        
    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        '''
        important notes****
        - 0 indexed board (dimensions excluded)
        - board always starts with a '0' tile
        '''
        print("1")
        #UPDATE BOARD HERE
        self._board[self._move_x][self._move_y] = number

        heapq.heappush(self._frontier, (number, self._move_x, self._move_y)) # push previous move into priqueue
        tile_no, self._move_x, self._move_y = heapq.heappop(self._frontier) # pop based on tile_no


        neighbors = self._getNeighbors(self._move_x, self._move_y)
        unmarked_neighbors = self._UnMarkedNeighbors(neighbors)
        action_x, action_y = unmarked_neighbors[0]

        if tile_no == 0: # EffectiveLabel(x) == 0, but board is only 0's
            if len(unmarked_neighbors) != 1: # add to priqueue unmarked neighbors > 1
                heapq.heappush(self._frontier, (tile_no, self._move_x, self._move_y))
            #update moves:
            self._move_x = action_x
            self._move_y = action_y
            print(self._move_y, self._move_x)
            return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
        else:  # tile_no == 1 -> then no more zeroes
            print(action_y, action_x)
            self._board[action_x][action_y] = -1
            return Action(AI.Action.FLAG, action_x, action_y)
        ########################################################################
        #							YOUR CODE ENDS							   #
        ########################################################################

    def _NumUnMarkedNeighbors(self, unmarked_neighbors):
        return len(unmarked_neighbors)
    
    def _UnMarkedNeighbors(self, neighbors):
        '''returns list of unmarked neighbors
         - "unmarked" means undiscovered'''
        unmarked_neighbors = []
        for x,y in neighbors:
            if self._board[x][y] == None:
                unmarked_neighbors.append((x,y))
        return unmarked_neighbors


    def _getNeighbors(self, move_x, move_y) -> list[(int,int)]:
        '''returns list of coordinates of all neighbors'''
        "left boundary, right boundary, top boundary, bottom boundary"
        neighbors = []

        topNeighbors = move_x- 1 >= 0
        bottomNeighbors = move_x + 1 <= self._rowDimension
        leftNeighbors = move_y - 1 >= 0
        rightNeighbors = move_y + 1 <= self._colDimension

        if (rightNeighbors):
            neighbors.append((move_x, move_y + 1))
        if (leftNeighbors):
            neighbors.append((move_x, move_y - 1))
        if (topNeighbors):
            neighbors.append((move_x - 1, move_y))
            if (rightNeighbors):
                neighbors.append((move_x - 1, move_y + 1))
            if (leftNeighbors):
                neighbors.append((move_x - 1, move_y - 1))
        if (bottomNeighbors):
            neighbors.append((move_x + 1, move_y))
            if (rightNeighbors):
                neighbors.append((move_x + 1, move_y + 1))
            if (leftNeighbors):
                neighbors.append((move_x + 1, move_y - 1))

        return neighbors

