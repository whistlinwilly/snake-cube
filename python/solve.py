#!/usr/bin/python

import unittest
import copy
from simplejson import dumps  # for lazy deep equality testing

# Sample Snake Ascii Art!
# |X|X|X|
#     |X|X|
#       |X|
#       |X|X|
#         |X|
#         |X|X|
#           |X|X|X|
#               |X|
#               |X|X|
#                 |X|X|
#                   |X|
#                   |X|X|X|
#                       |X|
#                       |X|X|X|


# Possible snake representations

# width of each segment
sample_snake_block_form = [3, 2, 1, 2, 1, 2, 3, 1, 2, 2, 1, 3, 1, 3]

# an adjacency representation:
# f = forced/fixed
# a = adjacent
# s = start
sample_snake_adjacency_form = "sffaaffaffaaffafaaaffafafaf"

# Cube representation - We need to store either an empty space or a "direction" for sections
# of the snake that have no degrees of freedom (forced/ fixed sections).
# Directional encoding scheme:
#    E -> empty space
#   xX -> -+ X axis
#   yY -> -+ Y axis
#   zZ -> -+ Z axis


def init_cube():
    return [
        [
            ['E' for _ in xrange(3)]
            for _ in xrange(3)
        ] for _ in xrange(3)
    ]

# Helper data structure maps directional encoding to xyz index


encoding = {
    'x': 0,
    'X': 0,
    'y': 1,
    'Y': 1,
    'z': 2,
    'Z': 2,
}

# Helper data structures for adjacency moves. These take the form
# (position_index, delta, direction) for combining in adjacent_moves
# and iterating over in generate_next_move
adj_x = [(0, 1, 'X'), (0, -1, 'x')]
adj_y = [(1, 1, 'Y'), (1, -1, 'y')]
adj_z = [(2, 1, 'Z'), (2, -1, 'z')]

# Helper data structure maps direction to all adjacent moves
adjacent_moves = {
    'x': adj_y + adj_z,
    'X': adj_y + adj_z,
    'y': adj_x + adj_z,
    'Y': adj_x + adj_z,
    'z': adj_x + adj_y,
    'Z': adj_x + adj_y,
}

# Queue for next move to search
moves = []
solved = False
snake = ""

# The general idea here is to generate legal next move choices and add them to
# the queue to be processed.  If we empty the queue before reaching the end of
# the string, there are no possible solutions. A move takes the form (cube,
# snake_index, position).


def solve(_snake):
    if len(_snake) != 27 or _snake[0] != "s":
        return "Invalid"
    global moves, snake
    snake = _snake
    cube = init_cube()
    moves += generate_starting_moves(cube)
    while len(moves) > 0 and not solved:
        curMove = moves[0]
        # Dequeue
        moves = moves[1:]
        moves += generate_next_move(curMove)
    if solved:
        return "Solveable!"
    else:
        return "Invalid"

# This is a little tricky because cubes have so many axes of symmetry. In
# reality the only unique starting positions are corner (in one direction),
# middle edge (in one direction along the face, and one direction towards any
# corner) or "face center" (in two directions, orthogonal to the plane/towards
# the center and parallel to the plane / along the face).  We will use:
# - (0,0,0) for the corner
# - (0,0,1) for the middle edge
# - (1,0,1) for the "face center"


def generate_starting_moves(cube):
    moves = []
    for p, d in [
        # Bottom left corner pointing towards +x, note that this is symmetrical to pointing along any positive axis
        ([0, 0, 0], 'X'),
        ([0, 0, 1], 'Y'),  # Bottom left "middle edge" pointing towards +y
        ([0, 0, 1], 'Z'),  # Bottom left "middle edge" pointing towards +z (corner)
        ([1, 0, 1], 'X'),  # "Face center" directed parallel to the plane along +x
        ([1, 0, 1], 'Y'),  # "Face center" directed orthogonally to the plane along +y
    ]:
        moves += [(add_to_cube(cube, p, d), 1, p)]
    return moves

# Return a modified cube where the position in the cube
# has been set to the passed direction


def add_to_cube(cube, position, direction):
    c = copy.deepcopy(cube)
    x, y, z = position
    c[x][y][z] = direction
    return c

# If we encounter a fixed piece, increment position in the correct direction,
# check that we are still within bounds, and set the position in the cube.


def generate_next_move(curMove):
    cube, snake_index, position = curMove
    print snake_index, len(snake)
    if snake_index == len(snake):
        global solved
        solved = True
        return []
    x, y, z = position
    direction = cube[x][y][z]
    if snake[snake_index] == 'f':
        delta = 1 if direction.isupper() else -1
        position[encoding[direction]] += delta
        if in_bounds(position):
            return [(add_to_cube(cube, position, direction), snake_index + 1, position)]
        else:
            return []
    if snake[snake_index] == 'a':
        next_moves = []
        for pos_index, delta, new_dir in adjacent_moves[direction]:
            new_pos = copy.deepcopy(position)
            new_pos[pos_index] += delta
            if in_bounds(new_pos):
                next_moves += [(add_to_cube(cube, new_pos, new_dir), snake_index + 1, new_pos)]
        return next_moves


def in_bounds(position):
    for i in [0, 1, 2]:
        if position[i] < 0 or position[i] > 2:
            return False
    return True


class SnakeTests(unittest.TestCase):
    def test(self):
        # add_to_cube
        c = add_to_cube(init_cube(), (1, 0, 0), 'X')
        assert dumps(c) != dumps(init_cube())
        assert c[1][0][0] == 'X'
        # solve
        self.assertEqual(solve("fff"), "Invalid")
        self.assertEqual(snake, "")
        self.assertEqual(solve(sample_snake_adjacency_form), "Solvable")  # temporary
        self.assertEqual(snake, sample_snake_adjacency_form)
