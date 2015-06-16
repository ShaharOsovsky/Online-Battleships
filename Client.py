__author__ = 'Alon Ben-Shimol and Shahar Osovsky'

import socket
import select
import sys
import Protocol
from Player import Player

EXIT_ERROR = 1
BOARD_SIZE = 10
OPPONENT_ANSWER = -1
CHECK_YOUR_BOARD = 0


class Client:

	# A Constructor for a client playing the battleship game, receving machine name and port,
	# player's name, and a list of his ships (it's indexes) as parameters
    def __init__(self, s_name, s_port, player_name, player_ships):

        self.server_name = s_name
        self.server_port = s_port
        
        self.player_name = player_name
        self.opponent_name = ""

        self.socket_to_server = None

        self.all_sockets = []
        self.player = Player(player_name, player_ships)
        self.latest_move = list()
        """
        If you want to run you program on windowns, you'll
        have to temporarily remove this line (but then you'll need
        to manually give input to your program). 
        """
        self.all_sockets.append(sys.stdin)  # DO NOT CHANGE

    def connect_to_server(self):

        # Create a TCP/IP socket_to_server
        try:
            self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:

            self.socket_to_server = None
            sys.stderr.write(repr(msg) + '\n')
            exit(EXIT_ERROR)

        server_address = (self.server_name, int(self.server_port))
        try:
            self.socket_to_server.connect(server_address)
            self.all_sockets.append(self.socket_to_server)  # this will allow us to use Select System-call

        except socket.error as msg:
            self.socket_to_server.close()
            self.socket_to_server = None
            sys.stderr.write(repr(msg) + '\n')
            exit(EXIT_ERROR)

        # we wait to get ok from server to know we can send our name
        num, msg = Protocol.recv_all(self.socket_to_server)
        if num == Protocol.NetworkErrorCodes.FAILURE:
            sys.stderr.write(msg)
            self.close_client()

        if num == Protocol.NetworkErrorCodes.DISCONNECTED:
            print "Server has closed connection."
            self.close_client()

        # send our name to server
        eNum, eMsg = Protocol.send_all(self.socket_to_server, sys.argv[3])
        if eNum:
            sys.stderr.write(eMsg)
            self.close_client()

        print "*** Connected to server on %s ***" % server_address[0] 
        print
        print "Waiting for an opponent..."
        print

    def close_client(self):
        print
        print "*** Goodbye... ***"
        self.socket_to_server.close()
        exit(0)

	# Handles the user's input, if the user wants to quit - it closes, else it
	# sends the user's massage to the server.
    def __handle_standard_input(self):
        msg = sys.stdin.readline().strip().upper()
        if msg == 'EXIT':  # user wants to quit
            eNum, eMsg = Protocol.send_all(self.socket_to_server, "PLAYER_QUIT_EXIT")
            if eNum:
                print eMsg
                self.close_client()
            self.close_client()
        else:
            return msg

	# Handles the massages coming from the server, whether it's errors, "EXIT" massages,
	# or plays or answers from the opposite client (player)
    def __handle_server_request(self):
        num, msg = Protocol.recv_all(self.socket_to_server)
        if num == Protocol.NetworkErrorCodes.FAILURE:
            sys.stderr.write(msg)
            self.close_client()

        if num == Protocol.NetworkErrorCodes.DISCONNECTED:
            print "Server has closed connection."
            self.close_client()
            
        if "EXIT" in msg:
            print "Your opponent has disconnected. You win!"
            self.close_client()

        if "start" in msg:
            self.__start_game(msg)
        
        else:
            msg_type = Client.server_msg_type(msg)  # Analyzing massage type
            #print "msg = " + msg				# ----------blllaaaaaaaaaaaaaaaaaaaaaa - ERASE
            if msg_type == OPPONENT_ANSWER:
                win = self.player.update_opponent_board(msg, self.latest_move[0], self.latest_move[1])
                self.print_board()
                if win:
                    #game ended - send massage
                    print "You won!"
                    self.close_client()
               
            else:	# A move was sent from the other client
                result = self.player.check_move(msg)
                Protocol.send_all(self.socket_to_server, result)    # Sends the response to the server
                print self.opponent_name + " plays: " + msg
                self.print_board()
                if "ALL" in result:
                    print "You lost :("
                    self.close_client()
                else:
                    print "It's your turn..."
    
    # The preparation for the game, receiving the opponent's name as parameter
    def __start_game(self, msg):
        
        print "Welcome " + self.player_name + "!"
        
        self.opponent_name = msg.split('|')[2]
        print "You're playing against: " + self.opponent_name + ".\n"
        self.print_board()
        if "not_turn" in msg:
            return
        
        print "It's your turn..."

    letters = list(map(chr, range(65, 65 + BOARD_SIZE)))

    # Prints both the player's and his opponent's board
    def print_board(self):
        print
        print "%s %56s" % ("My Board:", self.opponent_name + "'s Board:"),

        print
        print "%-3s" % "",
        for i in range(BOARD_SIZE):     # a classic case of magic number!
            print "%-3s" % str(i+1),

        print(" |||   "),
        print "%-3s" % "",
        for i in range(BOARD_SIZE):
            print "%-3s" % str(i+1),

        print

        for i in range(BOARD_SIZE):
            print "%-3s" % Client.letters[i],
            for j in range(BOARD_SIZE):
                print "%-3s" % self.player._board.get_cell_value([i, j]),

            print(" |||   "),
            print "%-3s" % Client.letters[i],
            for j in range(BOARD_SIZE):
                print "%-3s" % self.player._opponent_board.get_cell_value([i, j]),

            print
        
        print

	# Runs the game from the client's side (communicating with the server, and parsing it's 
	# massages using other functions.
    def run_client(self):
        while True:
            r_sockets = select.select(self.all_sockets, [], [])[0]  # We won't use writable and exceptional sockets

            if sys.stdin in r_sockets:
                move = self.__handle_standard_input()
                eNum, eMsg = Protocol.send_all(self.socket_to_server, move)
                if eNum:
                    print eMsg
                    self.close_client()
                self.latest_move = Client.parse_msg(move)

            elif self.socket_to_server in r_sockets:
                self.__handle_server_request()

	# Checks whether the msg given as parameter is a move made by the opponent (returns 0),
	# or the opponent's answer to this client's move (returns -1)
    @staticmethod
    def server_msg_type(msg):
        if ("HIT" in msg) or ("MISS"in msg) or ("SANK" in msg):
            return OPPONENT_ANSWER
        else:
            return CHECK_YOUR_BOARD

    # Parses the given massage string into a cell in the game board [i, j]
    @staticmethod
    def parse_msg(msg):
        move = msg.split(" ")
        attack_index = [ord(move[0].lower()) - 97, int(move[1]) - 1]
        return attack_index


def main():

    client = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
    client.connect_to_server()
    client.run_client()


if __name__ == "__main__":
    main()
