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

        self._flags = set()
        self._pending_flags = set()

        self._frontier = []

        self._safe = set()
        
        self._remaining_unmarked_cells = []

        self._all_mines_identified = False

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

        if self._all_mines_identified:
        #put a flag if mine is identified.
        #put a neighbors of identified mine.
            if self._remaining_unmarked_cells:
                move = self._remaining_unmarked_cells.pop()
                self._move_x = move[0]
                self._move_y = move[1]
                return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
            return Action(AI.Action.LEAVE)


        #UPDATE EFFECTIVE LABEL of self._move_x, self._move_y HERE

        heapq.heappush(self._frontier, (self._getFrontierPriority(self._move_x, self._move_y), self._move_x, self._move_y))

        unmarked_neighbors = []

        while not unmarked_neighbors and self._frontier:
            tile_no, self._move_x, self._move_y = heapq.heappop(self._frontier)
            neighbors = self._getNeighbors(self._move_x, self._move_y)
            unmarked_neighbors = self._UnMarkedNeighbors(neighbors)

        #UPDATE EFFECTIVE LABEL OF POPPED self._move_x, self._move_y HERE BASED ON NUMBER OF NEARBY FLAGS.

        #effective label == 0
        if self._board[self._move_x][self._move_y] == 0:
            #all cells are safe.
            for neighbor in unmarked_neighbors:
                self._safe.add(neighbor)

        #effective label == len(UnMarkedNeighbors)
        elif self._board[self._move_x][self._move_y] == len(unmarked_neighbors):
            for mine in unmarked_neighbors:
                mine_x, mine_y = mine
                self._flags.add((mine_x, mine_y))
                self._pending_flags.add((mine_x, mine_y))
                neighbors_of_mine = self._getNeighbors(mine_x, mine_y)
                for neighbor_x, neighbor_y in neighbors_of_mine:
                    if self._board[neighbor_x][neighbor_y] is not None:
                        heapq.heappush(self._frontier, (self._getFrontierPriority(neighbor_x, neighbor_y), neighbor_x, neighbor_y))

        if len(self._flags) == self._total_mines:
            #all mines identified
            self._remaining_unmarked_cells = self._getUnMarkedCell()
            self._all_mines_identified = True

        if self._safe:
            self._move_x, self._move_y = self._safe.pop()
            return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
        
        if self._pending_flags:
            self._move_x, self._move_y = self._pending_flags.pop()
            return Action(AI.Action.FLAG, self._move_x, self._move_y)

        #RETURN RANDOM ACTION HERE
        return Action(AI.Action.LEAVE)
        ########################################################################
        #                           YOUR CODE ENDS                              #
        ########################################################################

    def _getFrontierPriority(self, move_x, move_y):
        unmarked_neighbors = self._UnMarkedNeighbors(self._getNeighbors(move_x, move_y))
        effective_label = self._board[move_x][move_y]
        return min(effective_label, len(unmarked_neighbors) - effective_label)

    def _getUnMarkedCell(self):
        unmarked_cells = []
        for x in range(self._rowDimension):
            for y in range(self._colDimension):
                if self._board[x][y] is None and (x, y) not in self._flags:
                    unmarked_cells.append((x, y))
        return unmarked_cells

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
