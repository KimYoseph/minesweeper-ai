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

        self._mine_x = None
        self._mine_y = None 

        self._frontier = []

        self._covered = set() # a set of safe covered blocks to uncover after mine has been identified.
        self._mine_identified = False
        self._completed = False 

        ########################################################################
        #							YOUR CODE ENDS							   #
        ########################################################################

        
    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        #                           YOUR CODE BEGINS                            #
        ########################################################################
        '''
        important notes****
        - 0 indexed board (dimensions excluded)
        - board always starts with a '0' tile
        '''

        if self._completed:
            return Action(AI.Action.LEAVE)

        if self._mine_identified:
            if self._covered:
                move = self._covered.pop()
                self._move_x = move[0]
                self._move_y = move[1]
                return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
            self._completed = True 
            return Action(AI.Action.UNFLAG, self._mine_x, self._mine_y)
        

        # UPDATE BOARD HERE
        self._board[self._move_x][self._move_y] = number
        heapq.heappush(self._frontier, (number, self._move_x, self._move_y))
        unmarked_neighbors = []

        while not unmarked_neighbors and self._frontier:
            tile_no, self._move_x, self._move_y = heapq.heappop(self._frontier)
            neighbors = self._getNeighbors(self._move_x, self._move_y)
            unmarked_neighbors = self._UnMarkedNeighbors(neighbors)

        action_x, action_y = unmarked_neighbors[0]

        if tile_no == 0: # EffectiveLabel(x) == 0, but board is only 0's
            if len(unmarked_neighbors) != 1:
                heapq.heappush(self._frontier, (tile_no, self._move_x, self._move_y))

            self._move_x = action_x
            self._move_y = action_y

            return Action(AI.Action.UNCOVER, self._move_x, self._move_y)

        else: # tile_no == 1 -> then no more zeroes
            '''
            This block is to gather covered neighbors and is executed only
            for the first time position with tile_no == 1 is popped from priority queue above.
            '''
            unmarked_neighbors_set = set(unmarked_neighbors) 
            mine = unmarked_neighbors_set.copy()
            self._covered = unmarked_neighbors_set.copy()

            while self._frontier:
                tile_no, move_x, move_y = heapq.heappop(self._frontier)
                if tile_no != 1:
                    continue
                neighbors = self._getNeighbors(move_x, move_y)
                unmarked_neighbors = self._UnMarkedNeighbors(neighbors)
                unmarked_neighbors_set = set(unmarked_neighbors)
                if (len(mine) > 1):
                    mine &= unmarked_neighbors_set
                self._covered |= unmarked_neighbors_set

            for x, y in self._covered.copy():
                neighbors = self._getNeighbors(x, y)
                #Expand self._covered by covered neighbors of covered neighbors of 1's
                self._covered |= set(self._UnMarkedNeighbors(neighbors)) 

            if len(mine) == 1:
                '''
                If there are no more tile_no == 0 blocks to expand,
                a mine has to be adjacent to every 1's that has been uncovered, and mine should be identifiable at this point.
                '''
                self._mine_identified = True

                self._covered -= mine

                move = mine.pop()
                
                self._mine_x = move[0]
                self._mine_y = move[1]

                self._board[move[0]][move[1]] = -1
                return Action(AI.Action.FLAG, move[0], move[1])

            return Action(AI.Action.LEAVE)

        ########################################################################
        #                           YOUR CODE ENDS                              #
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
        bottomNeighbors = move_x + 1 < self._rowDimension
        leftNeighbors = move_y - 1 >= 0
        rightNeighbors = move_y + 1 < self._colDimension

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

