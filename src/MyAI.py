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
        self._pending_actions = set() 
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
        print(self._pending_actions)
        print(self._frontier)
        if self._all_mines_identified:
        #put a flag if mine is identified.
        #put a neighbors of identified mine.
            if self._remaining_unmarked_cells:
                return self._clearBoard()

        self._updateBoard(number) #updates effective label according to last action (flag --> update neighbors, uncover --> update self)
        self._updateFrontier(number)

        # UPDATE EFFECTIVE LABEL OF POPPED self._move_x, self._move_y HERE BASED ON NUMBER OF NEARBY FLAGS.
        # **** doesn't work (effective label should already be represented on the board)
        #effective label == 0
        returning_action = None
        while returning_action == None: # ensure we always return an action
            unmarked_neighbors = [] 
            if not self._frontier:
                self._move_x, self._move_y = self._getRandomMove()
                returning_action = Action(AI.Action.UNCOVER, self._move_x, self._move_y)
                break

            while not unmarked_neighbors and self._frontier:
                tile_no, self._move_x, self._move_y = heapq.heappop(self._frontier)
                unmarked_neighbors = self._getUnMarkedNeighbors(self._move_x, self._move_y)

            if self._getEffectiveLabel(self._move_x, self._move_y) == 0:
                #all cells are safe.
                for x,y in unmarked_neighbors:
                    self._pending_actions.add((x,y, AI.Action.UNCOVER))

        #effective label == len(UnMarkedNeighbors)
            elif self._board[self._move_x][self._move_y] == len(unmarked_neighbors):
                for mine_x, mine_y in unmarked_neighbors:
                    self._flags.add((mine_x, mine_y))
                    self._pending_actions.add((mine_x, mine_y, AI.Action.FLAG))
                    neighbors_of_mine = self._getUnMarkedNeighbors(mine_x, mine_y)
                    for neighbor_x, neighbor_y in neighbors_of_mine:
                        heapq.heappush(self._frontier, (self._getFrontierPriority(neighbor_x, neighbor_y), neighbor_x, neighbor_y))
                        # something to note: --> potential duplicates within the priqueue. May or may not be an issue?

        if len(self._flags) == self._total_mines:
            #all mines identified
            self._remaining_unmarked_cells = self._getAllUnMarkedCell()
            self._all_mines_identified = True
        
        if self._pending_actions:
            move_x, move_y, ai_action = self._pending_actions.pop()
            returning_action = Action(ai_action, move_x, move_y)
        '''
        safe_guess = self._getSafeGuess()
        if safe_guess:
            self._move_x = safe_guess[0]
            self._move_y = safe_guess[1]
            return Action(AI.Action.UNCOVER, self._move_x, self._move_y)
        '''
        #RETURN RANDOM ACTION HERE
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
    
    def _updateFrontier(self,number):
        if number == -1:
            # add uncovered neighbors into the frontier (potential options available)
            neighbors = self._getNumberedNeighbors(self._move_x, self._move_y)
            for n_x,n_y in neighbors:
                heapq.heappush(self._frontier, (self._getEffectiveLabel(n_x, n_y), n_x ,n_y))
        else:
            heapq.heappush(self._frontier, (self._getEffectiveLabel(self._move_x,self._move_y), self._move_x, self._move_y))
    
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
            return None

        return min(candidate_risk, key=candidate_risk.get)
        
    def _getRandomMove(self):
        for x in range(self._rowDimension):
            for y in range(self._colDimension):
                if self._board[x][y] == None:
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
