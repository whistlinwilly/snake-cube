#!/usr/bin/python

import unittest
import copy
from simplejson import dumps # for lazy deep equality testing
import sys

# Sample Snake 1 Ascii Art!
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
sample_snake_block_form_1 = [3,2,1,2,1,2,3,1,2,2,1,3,1,3]
sample_snake_adjacency_form_1 = "sffaaafaafaaafafaaaafafafaf" # f = forced/fixed, a = adjacent s = start? feedback welcome

# Sample Snake 2 Ascii Art!
# |X|X|X|
#     |X|
#     |X|X|
#       |X|
#       |X|X|
#         |X|
#         |X|X|
#           |X|X|
#             |X|
#             |X|X|X|
#                 |X|
#                 |X|X|
#                   |X|
#                   |X|X|X|
#                       |X|
#                       |X|

sample_snake_block_form_2 = [3,1,2,1,2,1,2,2,1,3,1,2,1,3,1,1]
sample_snake_adjacency_form_2 = "sffafaafaafaaaafafafaafafaf"


# Cube representation - We need to store the "direction" of the piece at each position in order
# to calculate valid next moves for both fixed and adjacent blocks. Because the direction
# is only useful while solving the puzzle, we also need to store move numbers in a solution cube
# in order to replay the solution later.
# Directional encoding scheme:
# E -> empty space
# xX -> -+ X axis
# yY -> -+ Y axis
# zZ -> -+ Z axis
def init_cube():
	return ([[['E' for _ in xrange(3)] for _ in xrange(3)] for _ in xrange(3)], [[[-1 for _ in xrange(3)] for _ in xrange(3)] for _ in xrange(3)])  

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
snake = ""
debug = False
furthest_progress = 0

# Pretty print moves
def print_moves(moves):
	for move in moves:
		cube, solution, snake_index, position = move
		print "Move " + str(snake_index) + "@ " + str(position) + ":"
		for y in [2, 1, 0]:
			sys.stdout.write('\n')
			for z in range(3):
				sys.stdout.write('\t')
				for x in range(3):
					sys.stdout.write(cube[x][y][z])
			for z in range(3):
				sys.stdout.write('\t')
				for x in range(3):
					sys.stdout.write('{:02}'.format(solution[x][y][z]))
		print ""

# The general idea here is to generate legal next move choices and add them to the queue to be processed.
# If we empty the queue before reaching the end of the string, there are no possible solutions. A move
# takes the form (cube, solution, snake_index, position).
def solve(_snake):
	solved = False
	if len(_snake) != 27 or _snake[0] != "s":
		return "Invalid"
	global moves, snake
	snake = _snake
	cube, solution = init_cube()
	if debug:
		print "Ready to begin! Starting moves:"
		print_moves(generate_starting_moves(cube, solution))
	moves += generate_starting_moves(cube, solution)
	while len(moves) > 0:
		curMove = moves[0]
		# Dequeue
		moves = moves[1:]
		_, _, index, _ = curMove
		if index == len(snake):
			solved = True
			break
		moves += generate_next_move(curMove)
	if solved:
		print "\n\nSnake: " + snake 
		print_moves([curMove])
		return "Solveable!"
	else:
		return "Invalid"

# This is a little tricky because cubes have so many axis of symmetry. In reality the only unique
# starting positions are corner (in one direction), middle edge (in one direction along the face, and
# one direction towards any corner) or "face center" (in two directions, orthogonal to the plane/towards 
# the center and parallel to the plane / along the face).
# We will use (0,0,0) for the corner, (0,0,1) for the middle edge, and (1, 0, 1) for the "face center".
def generate_starting_moves(cube, solution):
	moves = []
	for p, d in [
			# Bottom left corner pointing towards +x, note that this is symmetrical to pointing along any positive axis
			 ([0,0,0], 'X'), 
			 ([0,0,1], 'Y'), # Bottom left "middle edge" pointing towards +y
			 ([0,0,1], 'Z'), # Bottom left "middle edge" pointing towards +z (corner)
			 ([1,0,1], 'X'), # "Face center" directed parallel to the plane along +x
			 ([1,0,1], 'Y'), # "Face center" directed orthogonally to the plane along +y
		]:
		cube, solution = add_to_cube(cube, solution, p, d, 0) 
		moves += [(cube, solution, 1, p)]
	return moves

# Return both a modified cube where the position in the cube
# has been set to the passed direction, and a modified solution
# where the position has been set to the passed move number.
def add_to_cube(cube, solution, position, direction, move_number):
	c = copy.deepcopy(cube)
	s = copy.deepcopy(solution)
	x, y, z = position
	c[x][y][z] = direction
	s[x][y][z] = move_number
	return c, s
	
# If we encounter a fixed piece, increment position in the correct
# direction, check that we are still within bounds and that the next
# position is empty, and set the position in the cube. If we
# encounter an adjacent piece, iterate through possible adjacent moves,
# making a copy of position incremented in the right direction and
# performing similar checks.
def generate_next_move(curMove):
	if debug:
		print "Current move: "
		print_moves([curMove])
	cube, solution, snake_index, position = curMove
	if snake_index == len(snake):
		global solved
		solved = True
		return []
	x, y, z = position
	direction = cube[x][y][z]
	if snake[snake_index] == 'f':
		delta = 1 if direction.isupper() else -1
		position[encoding[direction]] += delta
		if in_bounds(position) and empty(cube, position):
			c, s = add_to_cube(cube, solution, position, direction, snake_index)
			if debug:
				print "Next moves:"
				print_moves([(c, s, snake_index + 1, position)])
			return [(c, s, snake_index + 1, position)]
		else:
			if debug:
				print "No next moves"
			return []
	if snake[snake_index] == 'a':
		next_moves = []
		for pos_index, delta, new_dir in adjacent_moves[direction]:
			new_pos = copy.deepcopy(position)
			new_pos[pos_index] += delta
			if in_bounds(new_pos) and empty(cube, new_pos):
				c, s = add_to_cube(cube, solution, new_pos, new_dir, snake_index)
				next_moves += [(c, s, snake_index + 1, new_pos)]
		if debug:
			print "Next moves:"
			print_moves(next_moves)
		return next_moves

def empty(cube, position):
	x, y, z = position
	if cube[x][y][z] == 'E':
		return True
	return False

def in_bounds(position):
	for i in [0, 1, 2]:
		if position[i] < 0 or position[i] > 2:
			return False
	return True 
	
class SnakeTests(unittest.TestCase):
	def test(self):
		# add_to_cube
		cube, solution = init_cube()
		c, s = add_to_cube(cube, solution, (1,0,0), 'X', 0)
		assert dumps(c) != dumps(cube)
		assert c[1][0][0] == 'X'
		assert s[1][0][0] == 0
		# solve
		self.assertEqual(solve("fff"), "Invalid")
		self.assertEqual(snake, "")
		self.assertEqual(solve(sample_snake_adjacency_form_1), "Solveable!") 
		self.assertEqual(snake, sample_snake_adjacency_form_1)
		self.assertEqual(solve(sample_snake_adjacency_form_2), "Solveable!") 
