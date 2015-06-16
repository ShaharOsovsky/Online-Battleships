__author__ = 'Shahar Osovsky'


DEFAULT_VALUE = "*"
HIT = 1
MISS = -1
SHIP_SANK = 0
ALL_SHIPS_SANK = 2


class Board():
	# A constructor for a Battleship board, receiving dimentions as parameters (rows, cols)
	# and also the player's ships (list of list of indexes), which if not None will be
	# updated in the board
    def __init__(self, num_of_rows, num_of_cols, player_ships):
        self.table = [[DEFAULT_VALUE for i in xrange(10)] for j in xrange(10)]
        if player_ships != None:
			for ship in player_ships:
				for cell in ship:	# Going through all the indexes in which there are ships
					self.mark_as_ship(cell)

    # Checks whether a cell contains a ship, and if do returns HIT, returns MISS otherwise
    def check_cell(self, index):
        if self.get_cell_value(index) == "0":
            return HIT
        return MISS
	
	# Changes the cell value of the given index to "0" in case of there is a ship there
    def mark_as_ship(self, index):
        self.change_cell_value(index, '0')
	
    # Changes the cell value of the given index to "H" in case of a hit
    def mark_as_hit(self, index):
        self.change_cell_value(index, 'H')

    # Changes the cell value of the given index to "X" in case of a miss
    def mark_as_miss(self, index):
        self.change_cell_value(index, 'X')

    # Changes the cell value of the given index [row, col] to the given value
    def change_cell_value(self, index, value):
		self.table[index[0]][index[1]] = value

    # Returns the cell value at the given index [row, col]
    def get_cell_value(self, index):
		return self.table[index[0]][index[1]]

    # Checks whether a ship sank and returns True if so, False otherwise
    def is_ship_sunk(self, ship):
        for index in ship:
            if self.get_cell_value(index) != "H":
                return False
        return True

    # Mark the ship as sunk, meaning all neighboring cells must be marked with 'X'
    def mark_ship_as_sunk(self, ship):
        for index in ship:
            row = index[0]
            col = index[1]
            neighbors = self.create_neighbors_list(row, col)
            for cell in neighbors:
                if self.get_cell_value(cell) != 'H':
                    self.change_cell_value(cell, 'X')

    # Creates and returns a list of all the cell's neighbors (within the board's boundaries)
    def create_neighbors_list(self, row, col):
        neighbors = list()    
        for i in xrange(-1, 2):
			if 0 <= (col + i) < len(self.table[0]):
				if row > 0:
					neighbors.append([row - 1, col + i])
				if row < len(self.table) - 1:
					neighbors.append([row + 1, col + i])
				if i != 0:
					neighbors.append([row, col + i])
        return neighbors
