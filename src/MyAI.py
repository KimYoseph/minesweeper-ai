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
        self._frontier = []
        
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
            return self._clearBoard()
        # updates effective label according to last action (flag --> update neighbors, uncover --> update self)

        # UPDATE EFFECTIVE LABEL OF POPPED self._move_x, self._move_y HERE BASED ON NUMBER OF NEARBY FLAGS.
        # **** doesn't work (effective label should already be represented on the board)
        #effective label == 0
        self._updateBoard(number)
        self._updateFrontier(number)

        returning_action = None
        checked_tiles= set()
        
        while self._frontier and returning_action == None: # ensure we always return an action
            tile_no, move_x, move_y = heapq.heappop(self._frontier)
            unmarked_neighbors = self._getUnMarkedNeighbors(move_x, move_y)

            # effective label == 0
            if self._getEffectiveLabel(move_x, move_y) == 0 and unmarked_neighbors: # all cells are safe
                returning_action = self._makeMove(AI.Action.UNCOVER, move_x, move_y, unmarked_neighbors)
            #effective label == len(UnMarkedNeighbors)
            elif self._getEffectiveLabel(move_x, move_y) == len(unmarked_neighbors) and unmarked_neighbors:
                returning_action = self._makeMove(AI.Action.FLAG, move_x, move_y, unmarked_neighbors)
            else:
                checked_tiles.add((move_x, move_y))

        if len(self._flags) == self._total_mines: # check if board is finished
            #all mines identified
            self._remaining_unmarked_cells = self._getAllUnMarkedCell()
            self._all_mines_identified = True
            returning_action = self._clearBoard()
        
        if not self._frontier and returning_action == None: # check if we failed to get a playable move (have to use random moves)
            self._move_x, self._move_y = self._getSafeGuess()
            returning_action = Action(AI.Action.UNCOVER, self._move_x, self._move_y)
    
        while checked_tiles: # push back all moves into frontier
            move_x, move_y = checked_tiles.pop()
            heapq.heappush(self._frontier, (self._getEffectiveLabel(move_x, move_y), move_x, move_y))

        return returning_action

        ########################################################################
        #                           YOUR CODE ENDS                              #
        ########################################################################
    
    def _clearBoard(self):
        #put a flag if mine is identified.
        #put a neighbors of identified mine.
        if self._remaining_unmarked_cells:
            move = self._remaining_unmarked_cells.pop()
            self._move_x = move[0]
            self._move_y = move[1]
            return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
        return Action(AI.Action.LEAVE)
    
    def _updateBoard(self, number):
        self._board[self._move_x][self._move_y] = number

    def _updateFrontier(self, number):
        if number != -1:
            heapq.heappush(self._frontier, (self._getEffectiveLabel(self._move_x, self._move_y), self._move_x, self._move_y))

    def _makeMove(self, ai_action, move_x, move_y, unmarked_neighbors):
        if len(unmarked_neighbors) > 1: # if multiple actions available
            heapq.heappush(self._frontier, (self._getEffectiveLabel(move_x, move_y), move_x, move_y))
        self._move_x, self._move_y = unmarked_neighbors[0]
        if ai_action == AI.Action.FLAG:
            self._flags.add((self._move_x, self._move_y))
        return Action(ai_action, self._move_x, self._move_y)

    def _getEffectiveLabel(self, move_x, move_y):
        marked_neighbors = self._getMarkedNeighbors(move_x, move_y)
        return self._board[move_x][move_y] - len(marked_neighbors)

    def _getSafeGuess(self):
        '''
        Find unmarked (x, y) in lowest local maximum probability of being a mine.
        '''
        candidate_risk = {}

        for x in range(self._rowDimension):
            for y in range(self._colDimension):
                if self._board[x][y] is None or self._board[x][y] == -1:
                    continue

                unmarked = self._getUnMarkedNeighbors(x, y)
                if not unmarked:
                    continue

                effective_label = self._getEffectiveLabel(x, y)
                risk = effective_label / len(unmarked)

                for ux, uy in unmarked:
                    if (ux, uy) in self._flags:
                        continue

                    if (ux, uy) not in candidate_risk:
                        candidate_risk[(ux, uy)] = risk
                    else:
                        candidate_risk[(ux, uy)] = max(candidate_risk[(ux, uy)], risk)

        if not candidate_risk:
            return self._getRandomMove()

        return min(candidate_risk, key=candidate_risk.get)
        
    def _getRandomMove(self):
        for x in range(self._rowDimension):
            for y in range(self._colDimension):
                if self._board[x][y] == None and (x, y) not in self._flags:
                    return (x,y)

    def _getFrontierPriority(self, move_x, move_y):
        unmarked_neighbors = self._getUnMarkedNeighbors(move_x, move_y)
        effective_label = self._board[move_x][move_y]
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
    
