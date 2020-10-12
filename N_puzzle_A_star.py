import copy
from queue import PriorityQueue
import random
import time
import warnings
warnings.filterwarnings('ignore')

class Board:
    """A class representing a puzzle board

    Attributes:
        tiles (list): A 2D list representing tiles in the board, 
                            e.g., [[1,2,3],[4,5,6],[7,8,0]].
        parent (Board, default=None): The parent node of the current node in the search tree. 
                                    This attribute will only be used to print path.
        action (str, default=None): The action taken in the parent node and get the current node.
                                This attribute will only be used to print path.
        width (int): The width of the board, representing the problem scale.
        g (int): The depth of the current board node.
        h (int): The manhattan distance of all tiles to the goal positions.
        f (int): The evaluation function of A* algorithm, which equals g+h.
        NOTE: You can use any other distance to calculate h, even take any other formulation as the evaluation function. 
    """
    def __init__(self, tiles, parent=None, action=None):
        self.tiles = tiles
        self.width = len(tiles)
        self.parent = parent #print path
        self.action = action
        if parent is not None:
            self.g = parent.g + 1
        else:
            self.g = 0

    def neighbors(self, record_parent=False):
        """Get neighbors for the current board

        Args:
            self (Board): The current board object.
            record_parent (bool, default=False): Record parent information or not. When do BFS to solve puzzle, 
                                            we need to record parent information to get the entire path. If we 
                                            just shuffle the initial board, we don't need to do it.
        
        Returns:
            nbs (list): A list to store neighbor boards (Board instances) of the current board. 
                    Swapping the '0' tile with one of it's neighbor tiles will get an neighbor board.
        """
        nbs = []
        for i in range(self.width):
            for j in range(self.width):
                if(self.tiles[i][j] == 0):
                    if(i-1 >= 0):
                        tmp = copy.deepcopy(self.tiles)
                        tmp[i-1][j], tmp[i][j] = tmp[i][j], tmp[i-1][j]
                        nbs.append(Board(tmp, self, 'Down')) if record_parent else nbs.append(Board(tmp))
                    if(i+1 < self.width):
                        tmp = copy.deepcopy(self.tiles)
                        tmp[i+1][j], tmp[i][j] = tmp[i][j], tmp[i+1][j]
                        nbs.append(Board(tmp, self, 'Up')) if record_parent else nbs.append(Board(tmp))
                    if(j-1 >= 0):
                        tmp = copy.deepcopy(self.tiles)
                        tmp[i][j-1], tmp[i][j] = tmp[i][j], tmp[i][j-1]
                        nbs.append(Board(tmp, self, 'Right')) if record_parent else nbs.append(Board(tmp))
                    if(j+1 < self.width):
                        tmp = copy.deepcopy(self.tiles)
                        tmp[i][j+1], tmp[i][j] = tmp[i][j], tmp[i][j+1]
                        nbs.append(Board(tmp, self, 'Left')) if record_parent else nbs.append(Board(tmp))
        return nbs

    def manhattan(self):
        """Calculate manhattan distance of all tiles to the goal positions"""
        distance = 0
        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[i][j] != 0:
                    x, y = divmod(self.tiles[i][j]-1, self.width)
                    distance += abs(x - i) + abs(y - j)
        return distance

    @property
    def f(self):
        """Evaluation function in A* algorithm

        Based on this function, the algorithm can decide which board node to take as the next step.
        This function is decorated as property function, so it can also be called as an attribute.
        """
        self.h = self.manhattan()
        return self.g + self.h

    def path(self):
        """Get the path from initial board to the current board

        Args:
            self (Board): The current board object.
        
        Returns:
            path (list): A list of Board instances from initial board to the current board.
        """
        cur, path = self, []
        while cur:
            path.append(cur)
            cur = cur.parent
        return list(reversed(path))

    def shuffle(self, num):
        """Shuffle the board tiles

        NOTE: This method is just used to shuffle the goal board to get a puzzle board.

        Args:
            self (Board): The current board object.
            num (int): The number of steps to shuffle the tiles randomly. It will move only one tile in one step.
                    NOTE: This argument also implies degree of difficulty of the puzzle board.

        Returns:
            puzzle (Board): The puzzle board instance.
        """
        puzzle = self
        for _ in range(num):
            puzzle = random.choice(puzzle.neighbors())
        return puzzle
    
    def print_tiles(self):
        """Print the board tiles row by row

        Args:
            self (Board): The current board object.

        Returns:
            (None)
        """
        for row in self.tiles:
            print(row)

    def __repr__(self):
        """Override the python built-in function '__repr__()'

        Args:
            self (Board): The current board object.

        Returns:
            A string to represent the current board instance's tile distribution.
            e.g., "1 2 3 4 5 6 7 8 0"
        """
        return ' '.join(map(str, self))

    def __iter__(self):
        """Override the python built-in function '__iter__()'

        Make the board instance to be an iterable object.

        Args:
            self (Board): The current board object.

        Returns:
            An generator of each row of tiles.
        """
        for row in self.tiles:
            yield from row

    def is_solved(self):
        """Judge if the current board is solved

        Args:
            self (Board): The current board object.

        Returns:
            An bool value representing whether the current board equals the goal board.
        """
        N = self.width**2
        return self.__repr__() == (' '.join(map(str, range(1, N))) + ' 0')
    
    def __lt__(self, other):
        """Override the python built-in function __lt__()

        This function used to compare two Board object, which will be used in the priority queue.

        Args:
            self (Board): The current Board instance.
            other (Board): Other Board instance.
        
        Returns:
            Whether the 'self' instance's f property is less than the 'other' instance's f property.
        """
        return self.f < getattr(other, 'f', other)
    
    def __eq__(self, other):
        """Override the python built-in function __eq__()

        This function used to compare two Board object, which will be used in the priority queue.

        Args:
            self (Board): The current Board instance.
            other (Board): Other Board instance.
        
        Returns:
            Whether the 'self' instance's f property is equal to the 'other' instance's f property.
        """
        return self.f == getattr(other, 'f', other)

class Solver:
    """A solver class

    Attributes:
        puzzle (Board): The puzzle board to solve.    
    """

    def __init__(self, puzzle):
        self.puzzle = puzzle

    def solve(self):
        """Solve the puzzle board

        Perform a A* algorithm to find the answer.

        Args:
            self (Solver): The solver object.
        
        Returns:
            path (list): A list of Board instance from the puzzle board to the goal board.
        """
        q = PriorityQueue() # use a priority queue to find the best node (with the smallest f) to take
        q.put(self.puzzle)
        seen = set() # to avoid repetition
        seen.add(self.puzzle.__repr__())

        while not q.empty():
            node = q.get()
            if node.is_solved():
                return node.path()

            for nb in node.neighbors(record_parent=True):
                if nb.__repr__() not in seen:
                    q.put(nb)
                    seen.add(nb.__repr__())

def make_goal(s):
    """Generate a goal board with an given size

    Args:
        s (int, s>=3): The size of goal board to generate, i.e. the width of the board. 
    
    Returns:
        goal (list): A 2D list representing tiles of the goal board, 
                    e.g., if the size given is 3, the goal is [[1,2,3],[4,5,6],[7,8,9]].
    """
    goal = []
    arr = [i for i in range(1, s*s)]
    arr.append(0)
    for i in range(s):
        tmp = []
        for j in range(s):
            tmp.append(arr[i*s + j])
        goal.append(tmp)
    return goal

if __name__ == "__main__":
    # generate a puzzle board to solve
    puzzle = Board(make_goal(3)).shuffle(100)
    print("Puzzle to solve:")
    puzzle.print_tiles()
    print("\n----Begin!----\n")

    # generate a solver to solve the puzzle
    s = Solver(puzzle)
    t0 = time.clock()
    path = s.solve()
    t1 = time.clock()

    # print the resualts
    step = 0
    for node in path:
        if node.parent is not None:
            print(node.action) 
        node.print_tiles()
        print()
        step += 1

    print("Total number of steps: " + str(step))
    print("Total amount of time in search: " + str(t1 - t0) + " second(s)")