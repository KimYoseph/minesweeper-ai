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

        # tasks: 
        # - updating board (effective label)
        # - doing actions (when to uncover, when to pick mines)
        # - random action

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

        self._flags = set()
        self._pending_actions = set() #combined self._safe and self._pending_flags

        self._frontier = []
        self._numbered_cells = set()
        
        self._remaining_unmarked_cells = [] # empty until self._total_mines == len(self._flags)

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

        self._board[self._move_x][self._move_y] = number

        if number != None and number != -1:
            self._numbered_cells.add((self._move_x, self._move_y))

        if self._pending_actions:
            self._move_x, self._move_y, ai_action = self._pending_actions.pop()
            return Action(ai_action, self._move_x, self._move_y)
        
        unmarked_neighbors = []
        to_remove = set()
        mine_probs = {}
        for x, y in self._numbered_cells:
            unmarked_neighbors = self._getUnMarkedNeighbors(x, y)
            if (len(unmarked_neighbors) == 0):
                to_remove.add((x, y))
                continue

            effective_label = self._getEffectiveLabel(x, y)
            
            #effective label == 0
            if effective_label == 0:
                #all cells are safe.
                for neighbor_x, neighbor_y in unmarked_neighbors:
                    if (neighbor_x, neighbor_y) not in self._flags:
                        self._pending_actions.add((neighbor_x, neighbor_y, AI.Action.UNCOVER))
                to_remove.add((x, y))
            
            #effective label == len(UnMarkedNeighbors)
            elif effective_label == len(unmarked_neighbors):
                for mine_x, mine_y in unmarked_neighbors:
                    self._flags.add((mine_x, mine_y))
                    self._board[mine_x][mine_y] = -1
                    self._pending_actions.add((mine_x, mine_y, AI.Action.FLAG))
                to_remove.add((x, y))

            #update mine_prob
            for neighbor_x, neighbor_y in unmarked_neighbors:
                mine_prob = effective_label / len(unmarked_neighbors)
                if (neighbor_x, neighbor_y) not in mine_probs:
                    mine_probs[(neighbor_x, neighbor_y)] = mine_prob
                else:
                    mine_probs[(neighbor_x, neighbor_y)] = max(mine_probs[(neighbor_x, neighbor_y)], mine_prob)
        
        self._numbered_cells -= to_remove

        if len(self._flags) == self._total_mines:
            self._remaining_unmarked_cells = self._getAllUnMarkedCell()
            self._all_mines_identified = True

        if self._pending_actions:
            self._move_x, self._move_y, ai_action = self._pending_actions.pop()
            return Action(ai_action, self._move_x, self._move_y)

        if mine_probs:
            self._move_x, self._move_y = min(mine_probs, key=mine_probs.get)
            return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
        #RETURN RANDOM ACTION HERE
        self._move_x, self._move_y = self._getRandomMove()
        return Action(AI.Action.UNCOVER, self._move_x, self._move_y)

        ########################################################################
        #                           YOUR CODE ENDS                              #
        ########################################################################
    '''
    def _updateBoard(self, number):
        unmarked_neighbors = self._getUnMarkedNeighbors(self._move_x, self._move_y)
        marked_neighbors = self._getMarkedNeighbors(self._move_x, self._move_y)
        if number == -1:
            for n_x, n_y in unmarked_neighbors:
                self._board[n_x][n_y] -=1
        else:
            self._board[self._move_x][self._move_y] = number - len(marked_neighbors)
    '''
    def _getEffectiveLabel(self, move_x, move_y):
        marked_neighbors = self._getMarkedNeighbors(move_x, move_y)
        return self._board[move_x][move_y] - len(marked_neighbors)
        
    def _getRandomMove(self):
        for x in range(self._rowDimension):
            for y in range(self._colDimension):
                if self._board[x][y] == None and (x, y) not in self._flags:
                    return (x,y)

    def _getFrontierPriority(self, move_x, move_y):
        unmarked_neighbors = self._getUnMarkedNeighbors(move_x, move_y)
        effective_label = self._getEffectiveLabel(move_x, move_y)
        return min(effective_label, len(unmarked_neighbors) - effective_label)

    def _getAllUnMarkedCell(self):
        unmarked_cells = []
        for x in range(self._rowDimension):
            for y in range(self._colDimension):
                if self._board[x][y] is None and (x, y) not in self._flags:
                    unmarked_cells.append((x, y))
        return unmarked_cells

    def _getNumberedNeighbors(self, move_x, move_y):
        neighbors = self._getNeighbors(move_x, move_y)
        numbered_neighbors = []
        for x,y in neighbors:
            if self._board[x][y] != -1 and self._board[x][y] != None:
                numbered_neighbors.append((x, y))
        return numbered_neighbors
    
    def _getMarkedNeighbors(self, move_x, move_y):
        ''' returns list of flagged neighbors'''
        neighbors = self._getNeighbors(move_x, move_y)
        marked_neighbors = []
        for x,y in neighbors:
            if self._board[x][y] == -1:
                marked_neighbors.append((x,y))
        return marked_neighbors
    
    def _getUnMarkedNeighbors(self, move_x, move_y):
        '''returns list of unmarked neighbors
         - "unmarked" means undiscovered'''
        neighbors = self._getNeighbors(move_x, move_y)
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
