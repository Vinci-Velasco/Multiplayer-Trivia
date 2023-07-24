# PLACEHOLDER - just for testing

import socket
import time
from lib import Tokens, parse_message, send

HOST = "127.0.0.1"
PORT = 7070

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
    my_socket.connect((HOST, PORT))

    BUFFER_SIZE = 1024
    
    player_number = -1
    host = False

    # Let the server know that a player has joined
    send(my_socket, Tokens.Player_Join)
    
    while True:
        # Wait for messages from the server and handle them
        message = my_socket.recv(BUFFER_SIZE).decode("utf8")
        token, data = parse_message(message)

        match token:
            case Tokens.Message:
                # For general messages sent from the server
                print(data)
            case Tokens.Begin_Vote:
                # Start voting for host after all players are ready
                host_vote = int(input(f"Vote for host (0-{int(data) - 1}): "))
                send(my_socket, f"{Tokens.Vote_Host} {host_vote}")
            case Tokens.Host_Choice:
                # Get the chosen host from the server
                if (player_number == int(data)):
                    host = True
                    print("You are the host!")
                else:
                    print(f"Player {data} is the host!")
            case Tokens.Player_Number:
                # Get player number from the server
                print(f"You are player {data}")
                player_number = int(data)
            case Tokens.Ready_Up:
                # Prompt user to ready up
                ready = False
                while not ready:
                    ready = input("Ready up? (y/n): ").lower() == "y"
                    if ready:
                        send(my_socket, Tokens.Ready_Up)
                        print("Waiting for players to ready up...")
