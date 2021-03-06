__author__ = 'Alon Ben-Shimol and Shahar Osovsky'

import socket
import select
import sys


import Protocol

MAX_CONNECTIONS = 2  # DO NOT CHANGE
ERROR_EXIT = 1


class Server:

    def __init__(self, s_name, s_port):
        self.server_name = s_name
        self.server_port = s_port

        self.l_socket = None
        self.players_sockets = []
        self.players_names = []

        self.all_sockets = []
        # By default it's the first player's turn in the beginning
        self.turn = 0
        
        """
        If you want to run you program on windows, you'll
        have to temporarily remove this line (but then you'll need
        to manually give input to your program). 
        """
        self.all_sockets.append(sys.stdin)
        


    def connect_server(self):

        # Create a TCP/IP socket_to_server
        try:
            self.l_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.l_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # DP NOT CHANGE
        except socket.error as msg:

            self.l_socket = None
            sys.stderr.write(repr(msg) + '\n')
            exit(ERROR_EXIT)

        server_address = (self.server_name, int(self.server_port))
        try:
            self.l_socket.bind(server_address)
            self.l_socket.listen(MAX_CONNECTIONS)
            self.all_sockets.append(self.l_socket)  # this will allow us to use Select System-call
        except socket.error as msg:
            self.l_socket.close()
            self.l_socket = None
            sys.stderr.write(repr(msg) + '\n')
            exit(ERROR_EXIT)

        print "*** Server is up on %s ***" % server_address[0]
        print

    # Closes all sockets and exits the program
    def shut_down_server(self):
        print
        print "*** Server is down ***"
        for socket in self.all_sockets:
            socket.close()
        exit(0)

	# Handles the input entered to the server, only in case of "EXIT" it shuts the server down
    def __handle_standard_input(self):
        
        msg = sys.stdin.readline().strip().upper()
        
        if msg == 'EXIT':
            self.shut_down_server()


    def __handle_new_connection(self):
        
        connection, client_address = self.l_socket.accept()

        # Request from new client to send his name
        eNum, eMsg = Protocol.send_all(connection, "ok_name")
        if eNum:
            sys.stderr.write(eMsg)
            self.shut_down_server()
        
        ################################################
        
        
        # Receive new client's name
        num, msg = Protocol.recv_all(connection)
        if num == Protocol.NetworkErrorCodes.FAILURE:
            sys.stderr.write(msg)
            self.shut_down_server()

        if num == Protocol.NetworkErrorCodes.DISCONNECTED:

            sys.stderr.write(msg)
            self.shut_down_server()
        
        self.players_names.append(msg)

        self.players_sockets.append(connection)
        self.all_sockets.append(connection)
        print "New client named '%s' has connected at address %s." % (msg,client_address[0])

        if len(self.players_sockets) == 2:  # we can start the game
            self.__set_start_game(0) 
            self.__set_start_game(1)



    def __set_start_game(self, player_num):

        welcome_msg = "start|turn|" + self.players_names[1] if not player_num else "start|not_turn|" + self.players_names[0]
        
        eNum, eMsg = Protocol.send_all(self.players_sockets[player_num], welcome_msg)
        if eNum:
            sys.stderr.write(eMsg)
            self.shut_down_server()
                                
	# Handles the communication between the two clients, receiving information from one, analyzing
	# it, and sends it to the other, and vice versa.
    def __handle_existing_connections(self):
        # IF no_errors then:
		
        # Gets the player's move (who's turn is up)
        num, msg = Protocol.recv_all(self.players_sockets[self.turn])
        if num == Protocol.NetworkErrorCodes.DISCONNECTED:
            Protocol.send_all(self.players_sockets[1 - self.turn], 'EXIT')
            self.shut_down_server()
        # Sends the move to his opponent
        if num != Protocol.NetworkErrorCodes.FAILURE:
			eNum, eMsg = Protocol.send_all(self.players_sockets[1 - self.turn], msg)
			if eNum == Protocol.NetworkErrorCodes.FAILURE:
				Protocol.send_all(self.players_sockets[self.turn], 'EXIT')
				self.shut_down_server()
			# Receives the opponent's response
			num, msg = Protocol.recv_all(self.players_sockets[1- self.turn])
			if num == Protocol.NetworkErrorCodes.FAILURE:
				print msg
				self.shut_down_server()
			if num == Protocol.NetworkErrorCodes.DISCONNECTED:
				Protocol.send_all(self.players_sockets[self.turn], 'EXIT')
				self.shut_down_server()
			# Sends the response back to the player who's turn is up
			eNum, eMsg = Protocol.send_all(self.players_sockets[self.turn], msg)
			if eNum:
				print eMsg
				self.close_client()

    def run_server(self):
        while True:
            r_sockets = select.select(self.all_sockets, [], [])[0]  # We won't use writable and exceptional sockets

            if sys.stdin in r_sockets:
                self.__handle_standard_input()

            elif self.l_socket in r_sockets:
                self.__handle_new_connection()
                           

            elif self.players_sockets[0] in r_sockets or \
                 self.players_sockets[1] in r_sockets:
                
                    self.__handle_existing_connections()
                    self.turn = 1 - self.turn

def main():

    server = Server(sys.argv[1], int(sys.argv[2]))   
    server.connect_server()
    server.run_server()


if __name__ == "__main__":
    main()
