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
from collections import deque


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
        for i in range(colDimension): # (row by col filed with None)
            self._board.append([])
            for j in range(rowDimension):
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

        self._step = 0

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
        if number != -1:
            self._step += 1
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

            if not unmarked_neighbors: continue # doesn't belong in frontier

            # effective label == 0
            if self._getEffectiveLabel(move_x, move_y) == 0: # all cells are safe
                returning_action = self._makeMove(AI.Action.UNCOVER, move_x, move_y, unmarked_neighbors)
            #effective label == len(UnMarkedNeighbors)
            elif self._getEffectiveLabel(move_x, move_y) == len(unmarked_neighbors):
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
        return max(self._board[move_x][move_y] - len(marked_neighbors), 0)

    def _getInformativeNumberedCells(self) -> list:
        numbered_cells = []
        for x in range(self._colDimension):
            for y in range(self._rowDimension):
                if self._board[x][y] is None or self._board[x][y] == -1:
                    continue
                unmarked_neighbors = self._getUnMarkedNeighbors(x, y)

                if not unmarked_neighbors:
                    continue

                effective_label = self._getEffectiveLabel(x, y)

                if effective_label == 0 or effective_label == len(unmarked_neighbors):
                    continue
                numbered_cells.append((x, y))
        return numbered_cells

    def _getSafeGuess(self):
        numbered_cells = self._getInformativeNumberedCells()

        if not numbered_cells:
            #if there is no constraint, get random action instead of backtracking.
            return self._getRandomMove()

        clusters = self._find_clusters(numbered_cells)

        if not clusters:
            return self._getRandomMove()

        DEPTH_LIMIT = 18 
        MAX_SOLUTIONS = 500
        MAX_CLUSTERS = 25

        clusters = clusters[:MAX_CLUSTERS]

        best_cell = None
        best_prob = 2.0

        for cells in clusters:
            cells.sort(key=lambda cell: -len(self._getNumberedNeighbors(cell[0], cell[1])))
            cells = cells[:DEPTH_LIMIT]

            selected_cells = set(cells)

            solutions = []
            mine_counts = {cell: 0 for cell in cells}

            self._backtrack(
                cells=cells,
                selected_cells=selected_cells,
                assignment={},
                path=[],
                solutions=solutions,
                mine_counts=mine_counts,
                depth_limit=DEPTH_LIMIT,
                max_solutions=MAX_SOLUTIONS
            )

            if not solutions:
                continue

            total = len(solutions)

            for cell in cells:
                prob = mine_counts[cell] / total

                # Guaranteed safe move.
                if prob == 0:
                    return cell

                if prob < best_prob:
                    best_prob = prob
                    best_cell = cell

        return best_cell if best_cell is not None else self._getRandomMove()

    def _find_unmarked_cluster(self, start_numbered_cell):
        '''
        Find the set of unmarked cell that shares at least one numbered cell with one another in the set.
        "N": numbered cell
        "U": unmarked cell
        '''
        q = deque()
        q.append(("N", start_numbered_cell))

        visited_nodes = set()
        numbered_visited = set()
        unmarked_cluster = set()

        while q:
            node_type, cell = q.popleft()
            node = (node_type, cell)
            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            if node_type == "N":
                #from a numbered cell, add its unmarked neighbors to the queue if not visited.
                numbered_visited.add(cell)
                for neighbor in self._getUnMarkedNeighbors(cell[0], cell[1]):
                    unmarked_node = ("U", neighbor)
                    if unmarked_node not in visited_nodes:
                        q.append(unmarked_node)
            else: # node_type == "U"
                #from unmarked cell, add its numbered neighbors to the queue if not visited 
                unmarked_cluster.add(cell)
                for neighbor in self._getNumberedNeighbors(cell[0], cell[1]):
                    numbered_node = ("N", neighbor)
                    if numbered_node not in visited_nodes:
                        q.append(numbered_node)

        return numbered_visited, list(unmarked_cluster)


    def _find_clusters(self, numbered_cells):
        visited_numbered = set()
        clusters = []

        for cell in numbered_cells:
            if cell in visited_numbered:
                continue
            numbered_visited, cluster = self._find_unmarked_cluster(cell)
            if cluster:
                clusters.append(cluster)
            visited_numbered.update(numbered_visited)
        return clusters

    def _choose_unassigned_cell(self, cells, assignment):
        best_cell = None
        best_score = -1

        for cell in cells:
            if cell in assignment:
                continue

            score = len(self._getNumberedNeighbors(cell[0], cell[1]))
            if score > best_score:
                best_score = score
                best_cell = cell

        return best_cell

    def _check_local_constraints(self, assignment, selected_cells, last_cell=None):
        numbered_cells_to_check = set()

        if last_cell is not None:
            numbered_cells_to_check.update(
                self._getNumberedNeighbors(last_cell[0], last_cell[1])
            )
        else:
            for cell in assignment:
                numbered_cells_to_check.update(
                    self._getNumberedNeighbors(cell[0], cell[1])
                )

        for nx, ny in numbered_cells_to_check:
            effective_label = self._getEffectiveLabel(nx, ny)
            unmarked_neighbors = self._getUnMarkedNeighbors(nx, ny)

            assigned_mines = 0
            unknown_cnt = 0

            for neighbor in unmarked_neighbors:
                if neighbor in assignment:
                    assigned_mines += assignment[neighbor]
                else:
                    unknown_cnt += 1

            if assigned_mines > effective_label:
                return False

            if assigned_mines + unknown_cnt < effective_label:
                return False

        remaining_mines = self._total_mines - len(self._flags)
        assigned_mine_count = sum(assignment.values())
        unassigned_in_cluster = len(selected_cells) - len(assignment)
        all_unmarked_count = len(self._getAllUnMarkedCell())
        outside_cluster_count = all_unmarked_count - len(selected_cells)

        if assigned_mine_count > remaining_mines:
            return False
        if outside_cluster_count == 0 and assigned_mine_count + unassigned_in_cluster < remaining_mines:
            return False

        return True

    def _check_all_constraints(self, assignment, selected_cells):
        numbered_cells_to_check = set()

        for cell in assignment:
            numbered_cells_to_check.update(
                self._getNumberedNeighbors(cell[0], cell[1])
            )

        for nx, ny in numbered_cells_to_check:
            effective_label = self._getEffectiveLabel(nx, ny)
            unmarked_neighbors = self._getUnMarkedNeighbors(nx, ny)

            assigned_mines = 0
            outside_or_unassigned = 0

            for neighbor in unmarked_neighbors:
                if neighbor in assignment:
                    assigned_mines += assignment[neighbor]
                else:
                    outside_or_unassigned += 1

            if outside_or_unassigned == 0:
                if assigned_mines != effective_label:
                    return False
            else:
                if assigned_mines > effective_label:
                    return False
                if assigned_mines + outside_or_unassigned < effective_label:
                    return False

        return True
            

    def _newBacktrack(self, cluster, depth_limit):
        # key idea is that we don't need multiple solutions. If we have one surefire solution, we just take it
        '''
        cluster: unmarked_neighbors of a cluster

        '''
        stack = []



    def _backtrack(self, cells, selected_cells, assignment, path,
               solutions, mine_counts, depth_limit, max_solutions):
        '''
        Recursive backtracking search.
        path stores previous/current nodes on this branch as ((x, y), value).
        value: 0 = SAFE, 1 = MINE.
        '''
        if len(solutions) >= max_solutions:
            return

        if len(assignment) == len(cells):
            if self._check_all_constraints(assignment, selected_cells):
                solutions.append(dict(assignment))
                for cell, value in assignment.items():
                    if value == 1:
                        mine_counts[cell] += 1
            return

        cell = self._choose_unassigned_cell(cells, assignment)
        if cell is None or len(assignment) >= depth_limit:
            return

        # Try SAFE first, then MINE.
        for value in [0, 1]:
            assignment[cell] = value
            path.append((cell, value))

            if self._check_local_constraints(assignment, selected_cells, cell):
                self._backtrack(
                    cells, selected_cells, assignment, path,
                    solutions, mine_counts, depth_limit, max_solutions
                )
            path.pop()
            del assignment[cell]
        
    def _getRandomMove(self):
        for x in range(self._colDimension):
            for y in range(self._rowDimension):
                if self._board[x][y] == None and (x, y) not in self._flags:
                    return (x,y)

    def _getFrontierPriority(self, move_x, move_y):
        unmarked_neighbors = self._getUnMarkedNeighbors(move_x, move_y)
        effective_label = self._board[move_x][move_y]
        return min(effective_label, len(unmarked_neighbors) - effective_label)

    def _getAllUnMarkedCell(self):
        unmarked_cells = []
        for x in range(self._colDimension):
            for y in range(self._rowDimension):
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
        bottomNeighbors = move_x + 1 < self._colDimension
        leftNeighbors = move_y - 1 >= 0
        rightNeighbors = move_y + 1 < self._rowDimension

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
    
