from math import floor, sqrt

# NOT IN USE ANYMORE
# from PIL import Image, ImageDraw, ImageFont
# class BgColors():
#     BLACK = '\033[30m'
#     RED = '\033[31m'
#     GREEN = '\033[32m'
#     YELLOW = '\033[33m'
#     BLUE = '\033[34m'
#     MAGENTA = '\033[35m'
#     CYAN = '\033[36m'
#     WHITE = '\033[37m'
#     UNDERLINE = '\033[4m'
#     RESET = '\033[0m'

def color_text(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)
    # return "\033[48;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

class Maze:

    # map icons
    CHAR_WALL = '🌴'
    CHAR_EMPTY = '👣'
    CHAR_ENEMY = '👹'
    CHAR_MINOR = '🐥'
    CHAR_PLAYER = '🐼'
    CHAR_GOAL = '🛖'
    # Path search related icons
    CHAR_TRAVELLED = '⭐️'
    CHAR_TO_VISIT = '❔'
    CHAR_VISITED = '❌'

    # To store our maze 2D array
    maze_map = []
    heuristic_map = []

    start_pos = ()
    goal_pos = ()
    size = ()

    # Cost for walls or objects that are impossible to cross
    UNAFFORDABLE_COST = 1000
    ENEMY_COST = 150
    MINOR_COST = 50

    # Rules for moving in the map
    ALLOWED_MOVES = (
        (1, 0),  # go right
        (0, 1),  # go down
        (0, -1),  # go up
        (-1, 0),  # go left
    )

    def __init__(self, file=None, maze_map=[]):
        self.maze_map = maze_map
        if file:
            self.parse_file(file)

        if len(self.maze_map) > 1 and len(self.maze_map[0]) > 1:
            self.pre_process()

    def parse_file(self, file):
        y = 0
        with open(file, 'r') as file:
            for line in file:
                x = 0
                _line = []
                line = line.strip()
                for c in line:
                    if c == 'S':
                        self.start_pos = (x, y)
                    elif c == 'G':
                        self.goal_pos = (x, y)
                    _line.append(c)
                    x += 1
                y += 1
                self.maze_map.append(_line)
        self.size = (len(self.maze_map[0]), len(self.maze_map))
        print(f"Parsed '{file.name}' as a {self.size[0]}x{self.size[1]} map.")

    # Generate heuristics
    def pre_process(self):

        self.heuristic_map = [[0 for i in range(self.size[0])] for j in range(self.size[1])]

        # print(len(self.maze_map), len(self.maze_map[0]))
        # print(self.size[1], self.size[0])

        for y in range(0, self.size[1]):

            for x in range(0, self.size[0]):

                c = self.maze_map[y][x]

                cost = self.heuristic_map[y][x]

                # this is a wall
                if c == '*':
                    cost = self.UNAFFORDABLE_COST
                else:
                    # calculate euclidean distance based cost from goal to current point
                    _dist_cost = sqrt((self.goal_pos[0] - x) ** 2 + (self.goal_pos[1] - y) ** 2)
                    # print(self.start_pos, (x, y), _dist_cost)
                    cost += _dist_cost

                    # The start position
                    if c == 'S':
                        self.start_pos = (x, y)
                    # the goal or end position
                    elif c == 'G':
                        self.goal_pos = (x, y)
                    # A dangerous enemy!
                    elif c == 'E':
                        cost += self.ENEMY_COST
                        self.heuristic_map[y - 1][x] += self.ENEMY_COST
                        self.heuristic_map[y - 1][x - 1] += self.ENEMY_COST
                        self.heuristic_map[y - 1][x + 1] += self.ENEMY_COST
                        self.heuristic_map[y + 1][x] += self.ENEMY_COST
                        self.heuristic_map[y + 1][x - 1] += self.ENEMY_COST
                        self.heuristic_map[y + 1][x + 1] += self.ENEMY_COST
                        self.heuristic_map[y][x - 1] += self.ENEMY_COST
                        self.heuristic_map[y][x + 1] += self.ENEMY_COST

                    # a minor enemy
                    elif c == 'e':
                        cost += self.MINOR_COST
                        self.heuristic_map[y - 1][x] += self.MINOR_COST
                        self.heuristic_map[y - 1][x - 1] += self.MINOR_COST
                        self.heuristic_map[y - 1][x + 1] += self.MINOR_COST
                        self.heuristic_map[y + 1][x] += self.MINOR_COST
                        self.heuristic_map[y + 1][x - 1] += self.MINOR_COST
                        self.heuristic_map[y + 1][x + 1] += self.MINOR_COST
                        self.heuristic_map[y][x - 1] += self.MINOR_COST
                        self.heuristic_map[y][x + 1] += self.MINOR_COST

                # set total cost to the position
                self.heuristic_map[y][x] = cost

                # print('--')


            # print(self.heuristic_map[y])

        # print(self.heuristic_map)

    def get_cost_at_position(self, position: tuple):
        return self.heuristic_map[position[1]][position[0]]

    def print_heuristics(self):
        print('Heuristic cost map')
        for line in self.heuristic_map:

            for cost in line:

                if cost > 0:
                    _max_value = 250
                    _scale = int(floor((min((cost, _max_value)) / _max_value) * 255))
                    # print(_scale)
                    print(color_text(_scale, 0, 50, u"\u2589"), end='')
                else:
                    print(color_text(0, 0, 50, u"\u2578"), end='')
            print()


    def print_maze(self, path=None, step=0, to_visit_nodes=None, visited_nodes=None, save_image=False):
        """

        :param path: optional path to visualized
        :param step: viz up to step in the path starting 1. 0 will show all the path
        :param to_visit_nodes: optionally visualize nodes to visit
        :param visited_nodes: optionally visualize nodes already visited
        :param save_file: Save output to an image
        :return:
        """

        output_str = ''

        maze_map = self.maze_map.copy()

        if to_visit_nodes:
            for node in to_visit_nodes:
                maze_map[node.position[1]][node.position[0]] = '?'

        if visited_nodes:
            for node in visited_nodes:
                maze_map[node.position[1]][node.position[0]] = 'x'

        # path available to print, if not print initial map
        if path:

            # if step is 0, visualize all the path
            if step == 0:
                step = len(path)

            # we update the maze with the path
            for i in range(0, step):
                pos = path[i]
                maze_map[pos[1]][pos[0]] = '.'

            # last position of the path is always the player
            pos = path[step-1]
            maze_map[pos[1]][pos[0]] = 'S'



        x, y = 0, 0
        for line in maze_map:
            for c in line:
                # this is a wall
                if c == '*':
                    _char_to_print = self.CHAR_WALL
                # The start position
                elif c == 'S':
                    _char_to_print = self.CHAR_PLAYER
                # the goal or end position
                elif c == 'G':
                    _char_to_print = self.CHAR_GOAL
                # A dangerous enemy!
                elif c == 'E':
                    _char_to_print = self.CHAR_ENEMY
                # a less dangerous enemy...
                elif c == 'e':
                    _char_to_print = self.CHAR_MINOR
                # this is to print a position travelled in a path for resolved mazes
                elif c == '.':
                    _char_to_print = self.CHAR_TRAVELLED
                elif c == '?':
                    _char_to_print = self.CHAR_TO_VISIT
                elif c == 'x':
                    _char_to_print = self.CHAR_VISITED
                # empty space
                else:
                    _char_to_print = self.CHAR_EMPTY

                output_str += _char_to_print
                # print(_char_to_print, end='')
                x += 1

            # print()
            output_str += '\n'
            y += 1

        print(output_str)

        # Tried to save image with emojis but are not colored and font dependent
        # if save_image:
        #     img = Image.new('RGB', (100, 30), color=(73, 109, 137))
        #     fnt = ImageFont.truetype('/Library/Fonts/Symbola.ttf', 15)
        #     d = ImageDraw.Draw(img)
        #     d.text((0, 0), output_str, font=fnt )
        #     # d.text((0, 0), output_str, fill=(255, 255, 0))
        #     img.save('images/output.png')

class PositionNode:

    def __init__(self, parent: "PositionNode", position: tuple):
        self.cost = 0
        self.parent: "PositionNode" = parent
        self.position: tuple = position

    def __eq__(self, other: "PositionNode"):
        return self.position == other.position

class MazeSolver:

    # to_visit = []
    # visited = []
    # maze = None

    MAX_ITER = 100000

    def __init__(self, maze: Maze):

        self.maze = maze


    def create_path_from_node(self, node):

        # list of positions
        path = []

        while node:
            path.append(node.position)

            node = node.parent

        # reverse the list, so the last node added is the first move
        path = path[::-1]
        return path

    def a_star_search(self):

        print('# Searching best path using A* ...')
        # Setup start and initialize
        start_node = PositionNode(None, self.maze.start_pos)
        end_node = PositionNode(None, self.maze.goal_pos)

        self.to_visit = []
        self.visited = []

        self.to_visit.append(start_node)

        # avoid infinite loop with maximum interations
        iteration = 1

        # main search loop while there are still nodes to visit
        while len(self.to_visit) > 0:

            current_node = self.to_visit[0]
            current_index = 0

            # # viz of the steps
            # print('---')
            # print("Iteration #", iteration)
            # _path = self.create_path_from_node(current_node)
            # self.maze.print_maze(path=_path, to_visit_nodes=self.to_visit, visited_nodes=self.visited)


            # iterate pending nodes to search lowest cost
            for i in range(len(self.to_visit)):
                node = self.to_visit[i]
                if node.cost < current_node.cost:
                    current_node = node
                    current_index = i

            iteration += 1
            if iteration > self.MAX_ITER:
                print(' - Error: Too many iterations...')
                # return partial result
                return self.create_path_from_node(current_node)

            # Remove from pending, and add to visited
            self.to_visit.pop(current_index)
            self.visited.append(current_node)

            # Check if we've found the goal!
            if current_node == end_node:
                print(f' - Done! after {iteration} steps. Total cost was {current_node.cost}')
                return self.create_path_from_node(current_node)


            # find children of current node in neighboring position using allowed moves

            for move in self.maze.ALLOWED_MOVES:

                # Calculate new position
                next_pos = (current_node.position[0] + move[0], current_node.position[1] + move[1])
                # get cost
                _cost = self.maze.get_cost_at_position(next_pos)

                # is it possible to move there?
                if _cost >= self.maze.UNAFFORDABLE_COST:
                    continue

                # Create new child node and add to the list
                child = PositionNode(current_node, next_pos)
                # calculate accumulated cost to move to that position
                child.cost = _cost + current_node.cost
                # children.append(child)

                # if the child is in the list AND the total cost is not lower, don't add again
                if len([i for i in self.to_visit if i == child and child.cost >= i.cost ]) > 0:
                    continue
                self.to_visit.append(child)


        # # self.to_visit.append(self.maze.start_pos)
        # # min_cost = self.maze.get_cost_at_position(self.maze.start_pos)
        # # current_index = 0
        #
        # for i in range(0, len(self.to_visit)):
        #
        #     pos = self.to_visit[i]
        #     _cost = self.maze.get_cost_at_position(pos)
        #     if _cost < min_cost:
        #         min_cost = self.maze.get_cost_at_position(pos)
        #         current_index = i
        #
        # current_pos = self.to_visit.pop(i)
        #
        # # we have founded to goal position
        # if current_pos == self.maze.goal_pos:
        #     return


if __name__ == '__main__':

    fn1 = 'maps/maze.txt'
    fn2 = 'maps/maze_small.txt'
    fn3 = 'maps/maze_breakpoint.txt'
    fn4 = 'maps/maze_breakpoint2.txt'

    # create the maze object
    maze = Maze(fn1)

    # print initial maze
    maze.print_maze()
    # print cost map
    maze.print_heuristics()

    # maze solver
    solver = MazeSolver(maze)
    path = solver.a_star_search()

    # print solution for all steps
    maze.print_maze(path, 0)

    # print solution step by step
    # for step in range(1, len(path)+1):
    #     print()
    #     print('Step:', step)
    #     maze.print_maze(path, step)
