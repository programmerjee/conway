import unittest
import numpy as np
import random

DEAD = 0
ALIVE = 1
ZOMBIE = 2
MUTATE_PROB = 0.0025

def get_neighbors(board, x, y):
	neighbors = []
	for y1 in range(-1, 2):
		for x1 in range(-1, 2):
			if x1 == 0 and y1 == 0:
				pass
			elif x + x1 < 0 or x + x1 >= board.shape[1]:
				pass
			elif y + y1 < 0 or y + y1 >= board.shape[0]:
				pass
			else:
				neighbors.append(board[y + y1, x + x1])
	return neighbors

def has_live_neighbors(board, x, y):
	neighbors = get_neighbors(board, x, y)
	for n in neighbors:
		if n == ALIVE:
			return True
	return False

def live_neighbor_count(board, x, y):
	neighbors = get_neighbors(board, x, y)
	live_neighbor_count = 0
	for n1 in neighbors:
		if n1 == ALIVE:
			live_neighbor_count = live_neighbor_count + 1
	return live_neighbor_count

def zombie_neighbor_count(board, x, y):
	neighbors = get_neighbors(board, x, y)
	zombie_neighbor_count = 0
	for n1 in neighbors:
		if n1 == ZOMBIE:
			zombie_neighbor_count = zombie_neighbor_count + 1
	return zombie_neighbor_count

def next_cell_state(board, x, y, rng = random.random):
	if board[y, x] == ZOMBIE:
		if has_live_neighbors(board, x, y):
			return ZOMBIE
		else:
			return DEAD
			
	if board[y, x] == DEAD:
		if live_neighbor_count(board, x, y) + zombie_neighbor_count(board, x, y) == 4:
			return ZOMBIE
		if live_neighbor_count(board, x, y) == 3:
			if rng.random() < MUTATE_PROB:
				return ZOMBIE
			return ALIVE
			
	if board[y, x] == ALIVE:
		if zombie_neighbor_count(board, x, y) >= 2:
			return ZOMBIE
		lnc = live_neighbor_count(board, x, y)
		if lnc == 2 or lnc == 3:
			return ALIVE
			
	return DEAD

def evolve(board, rng = random.random):
	new_board = np.zeros(board.size)
	for y in range(0, board.shape[0]):
		for x in range(0, board.shape[1]):
			board[x, y] = next_cell_state(board, x, y, rng)
	return board

class RNG():
	
	def __init__(self, return_value):
		self.return_value = return_value
	
	def random(self):
		return self.return_value

class ConwayTest(unittest.TestCase):

	def empty_grid(self, height, width):
		return np.zeros((height, width))

	def test_center_cell_has_eight_neighbors(self):
		board = self.empty_grid(3, 3)
		neighbor_list = get_neighbors(board, 1, 1)
		self.assertEqual(8, len(neighbor_list))
		
	def test_edge_cell_has_five_neighbors(self):
		board = self.empty_grid(3, 3)
		neighbor_list = get_neighbors(board, 1, 0)
		self.assertEqual(5, len(neighbor_list))
	
	def test_corner_cell_has_three_neighbors(self):
		board = self.empty_grid(3, 3)
		neighbor_list = get_neighbors(board, 0, 0)
		self.assertEqual(3, len(neighbor_list))
	
	def test_zombie_starves(self):
		board = self.empty_grid(3, 3)
		board[1, 1] = ZOMBIE
		new_state = next_cell_state(board, 1, 1)
		self.assertEqual(DEAD, new_state)
	
	def test_zombie_lives(self):
		board = self.empty_grid(3, 3)
		board[1, 1] = ZOMBIE
		board[0, 0] = ALIVE
		new_state = next_cell_state(board, 1, 1)
		self.assertEqual(ZOMBIE, new_state)

	def test_dead_cell_with_three_neighbors_comes_alive(self):
		board = self.empty_grid(3, 3)
		board[0, 0] = ALIVE
		board[0, 1] = ALIVE
		board[0, 2] = ALIVE
		new_state = next_cell_state(board, 1, 1, rng = RNG(0.1))
		self.assertEqual(ALIVE, new_state)
	
	def test_dead_cell_with_four_neighbors_comes_undead(self):
		board = self.empty_grid(3, 3)
		board[0, 0] = ALIVE
		board[0, 1] = ALIVE
		board[0, 2] = ALIVE
		board[1, 0] = ZOMBIE
		new_state = next_cell_state(board, 1, 1)
		self.assertEqual(ZOMBIE, new_state)

	def test_live_cell_with_two_zombie_neighbors_comes_undead(self):
		board = self.empty_grid(3, 3)
		board[1, 1] = ALIVE
		board[0, 0] = ZOMBIE
		board[0, 1] = ZOMBIE
		new_state = next_cell_state(board, 1, 1)
		self.assertEqual(ZOMBIE, new_state)
	
	def test_live_cell_with_three_zombie_neighbors_comes_undead(self):
		board = self.empty_grid(3, 3)
		board[1, 1] = ALIVE
		board[0, 0] = ZOMBIE
		board[0, 1] = ZOMBIE
		board[1, 2] = ZOMBIE
		new_state = next_cell_state(board, 1, 1)
		self.assertEqual(ZOMBIE, new_state)
	
	def test_live_cell_with_two_live_neighbors_stays_alive(self):
		board = self.empty_grid(3, 3)
		board[1, 1] = ALIVE
		board[0, 0] = ALIVE
		board[0, 1] = ALIVE
		new_state = next_cell_state(board, 1, 1)
		self.assertEqual(ALIVE, new_state)

	def test_dead_cell_mutates_to_zombie(self):
		board = self.empty_grid(3, 3)
		board[0, 0] = ALIVE
		board[0, 1] = ALIVE
		board[0, 2] = ALIVE
		new_state = next_cell_state(board, 1, 1, rng = RNG(0.0001))
		self.assertEqual(ZOMBIE, new_state)
	
	def test_dead_cell_doesnt_mutate(self):
		board = self.empty_grid(3, 3)
		board[0, 0] = ALIVE
		board[0, 1] = ALIVE
		board[0, 2] = ALIVE
		new_state = next_cell_state(board, 1, 1, rng = RNG(0.1))
		self.assertEqual(ALIVE, new_state)
	
	def test_evolve_static_1(self):
		board = self.empty_grid(4, 4)
		board[1, 1] = ALIVE
		board[1, 2] = ALIVE
		board[2, 1] = ALIVE
		board[2, 2] = ALIVE
		new_board = evolve(board)
		self.assertTrue(np.array_equal(board, new_board))
	
	def test_evolve_alternative(self):
		board = self.empty_grid(5, 5)
		board[1, 3] = ALIVE
		board[2, 3] = ALIVE
		board[3, 3] = ALIVE
		expected = self.empty_grid(5, 5)
		board[3, 1] = ALIVE
		board[3, 2] = ALIVE
		board[3, 3] = ALIVE
		self.assertTrue(np.array_equal(expected, evolve(board)))
		
if __name__ == '__main__':
	unittest.main()