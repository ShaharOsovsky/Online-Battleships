# Online-Battleships
An online simple battleships game initiated from 3 different terminals - one by the Server and two by Players. Written in Python.

DIRECTIONS:
-----------

In order to start the game from the Server side, -Run: python Server.py arg1 arg2

where:

arg1: the machine name – the machine name on which the server is running (or "127.0.0.1" to run it locally).

arg2: port number.



After the Server is running, the Clients can be activated:


In order to run the game from the Client sidem, -Run: python Client.py arg1 arg2 arg3 arg4

where:

arg1: the machine name - the machine on which the server(!) is running.

arg2: port number – the same used when opening a server(!).

arg3: the player's name.

arg4: *.ship file path – representing the player ships (I'll include a few example files).





EXAMPLE:
---------

1) On one terminal, go to where Server.py is located and type: python Server.py 127.0.0.1 8888. You've now opened a server (locally).

2) On a different terminal, go to where Client.py is located and type: python Client.py 127.0.0.1 8888 Shahar Ships/a.ship. This will open a client named Shahar and will connect him to the server you've just opened.

3) On yet another different terminal, type: python Client.py 127.0.0.1 8888 Nemesis Ships/b.ship. 


Now the game is on.

Type "exit" to leave the game at any given time.

When it'll be finished the connections will be closed (Server will end it's run).
