__author__ = 'Shahar Osovsky'

from Board import Board


class Player:
    NUM_OF_ROWS = 10
    NUM_OF_COLS = 10
    SHIP_NOT_FOUND = -1
    WIN = True
    GAME_ON = False
    HIT = 1

    # A constructor for a player in the Battleship game receiving a the player's name, and
    # a file containing the player's ships as parameter
    def __init__(self, player_name, player_ships):
        self._name = player_name
        self._ships = (Player.parse_ships(player_ships))[:]
        self._board = Board(Player.NUM_OF_ROWS, Player.NUM_OF_COLS, self._ships)
        self._opponent_board = Board(Player.NUM_OF_ROWS, Player.NUM_OF_COLS, None)
        self._opponent_ship_sank = list()

    # Parse the player's ships-file and returns a list containing each ship's indexes
    @staticmethod
    def parse_ships(player_ships):
        ships_file = open(player_ships)
        file_lines = ships_file.readlines()
        ships = [] * len(file_lines)
        for i in xrange(len(file_lines)):
		    ships.append([])
		    splitted_line = (file_lines[i].split(","))[:]
		    for cell in splitted_line:       # Separating the lines into indexes			
				ship_index = [ord(cell[0].lower()) - 97, int(cell[1:]) - 1]    # Parsing each cell
				ships[i].append(ship_index)
        return ships

    # Parses the given massage string into a cell in the game board ([row, col])
    @staticmethod
    def parse_move(move):
        move = move.split(" ")
        attack_index = [ord(move[0].lower()) - 97, int(move[1]) - 1]
        return attack_index

    # Returns a list with the indexes of the ship who covers the cell given as parameter [row,col]
    def find_ship(self, index):
        for i in xrange(len(self._ships)):
            for cell in self._ships[i]:
                if (cell[0] == index[0]) and (cell[1] == index[1]):
                    return self._ships[i]
        return Player.SHIP_NOT_FOUND

    # Adds to the _opponent_ship_sank list the indexes of the ship who covers the
    # given index, recursively.
    def find_opponent_ship(self, index):
        for i in xrange(-1, 2):
            for j in xrange(-1, 2):
                neighbor = (index[0] + i, index[1] + j)
                if 0 <= neighbor[0] <= 9 and 0 <= neighbor[1] <= 9:
                    if (neighbor not in self._opponent_ship_sank) and \
                                    self._opponent_board.get_cell_value(neighbor) == "H":
                        self._opponent_ship_sank.append(neighbor)

    # Checks the impact of the given move on this player's board, and updtes the board accordingly
    def check_move(self, move):
        index = Player.parse_move(move)[:]
        if self._board.check_cell(index) == Player.HIT:
            self._board.mark_as_hit(index)		# Marks the cell as HIT
            ship = self.find_ship(index)[:]
            if self._board.is_ship_sunk(ship):  # Checks if an entire ship was hit (hence sank)
                self._board.mark_ship_as_sunk(ship)		# Marks the ship as sunk
                if self.did_player_loose():    # Checks whether all the player's ship sank
                    return "ALL_SHIP_SANK"
                return "SHIP_SANK"
            return "HIT"
        self._board.mark_as_miss(index)		# Marks the cell as MISSED
        return "MISS"

    # Checks whether all the player's ships sank and returns True if so, False otherwise
    def did_player_loose(self):
        for ship in self._ships:
            if not self._board.is_ship_sunk(ship):
                return False
        return True

    # Updates the opponent's board according to the given opponent reponse
    def update_opponent_board(self, msg, row, col):
        if "MISS" in msg:
            self._opponent_board.mark_as_miss([row, col])
        elif "HIT" in msg:
            self._opponent_board.mark_as_hit([row, col])
        elif "SHIP" in msg:
            self._opponent_board.mark_as_hit([row, col])
            self.find_opponent_ship([row, col])
            self._opponent_board.mark_ship_as_sunk(self._opponent_ship_sank)
            if "ALL" in msg:
                return Player.WIN
        return Player.GAME_ON

    # Prints the player's board
    def print_board(self):
        print self._board
