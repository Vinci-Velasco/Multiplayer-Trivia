import socket
import threading
import time
import pickle
from queue import Queue
from src import player
from game import lobby_state

HOST = "127.0.0.1"
PORT = 7070

NUM_PLAYERS = 5

min_players = 3
max_players = 5

clients = {}

# Thread that deals with listening to clients
def listening_thread(client_socket, addr, message_queue):
    BUFFER_SIZE = 1024 # change size when needed
    with client_socket:
        while True:
            message = client_socket.recv(BUFFER_SIZE).decode("utf8")
            
            print(f"Recieved message from {addr}")
            # receive a ping
            if message == "ping":
                    client_socket.send("pong".encode('utf-8'))
            else:
                message_queue.put((message, addr))
            # client_socket.send("Server acknowledges your message\n".encode())
         
# Custom thread class that creates new threads once connections come in
class Recieve_Connection_Thread(threading.Thread):
    def __init__(self, server, message_queue):
        super().__init__()
        self.server = server
        self.message_queue = message_queue
        self.stop_connections = False

    # Listens to connections and creates new threads. Closes once max connections achieved
    # or stop_connections is set to True (via the stop() method)
    def run(self):
        connections = 0
        MAX_CONNECTIONS = 5

        while connections < MAX_CONNECTIONS:
            print(f"Listening for connections ({connections}/{MAX_CONNECTIONS})...")
            client_socket, addr = self.server.accept()

            # terminate thread if stop_connections set to True
            if self.stop_connections:
                break

            # otherwise create new thread for connection
            client_sockets.append(client_socket)
            client_addrs.append(addr)
            thread = threading.Thread(
                target=listening_thread, args=(client_socket, addr, self.message_queue))
            thread.start()
            connections += 1

           # Create a new Client and associated Player object, add to global dict
            global clients
            client_id = connections
            p = player.Player(client_id)
            c = Client(client_id, client_socket, addr, p)
            clients[client_id] = c

            PlayerNumber[addr] =  client_id, client_socket

            # client_socket.send(f"Connection to server established. You're Player #{connections}\n".encode("utf8"))

            # for client_socket in client_sockets:
               
            #     client_socket.send(str(f"Players: {client_addrs} are in the lobby!\n").encode("utf8"))


        print(f"Done with connections ({connections}/{MAX_CONNECTIONS})")


    # Stop the thread by changing the stop_connections cond to True and unblocking the
    # server.accept() call. This is safer than killing the thread as it can terminate properly
    def stop(self):
        self.stop_connections = True
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((HOST, PORT))

class Client():
    def __init__(self, id, socket, addr, player):
        self.id = id
        self.socket = socket
        self.addr = addr
        self.player_data = player # use Player class from src/player.py

def get_all_players():
    all_players = []
    for c in clients.values():
        all_players.append(c.player_data)
        
    return all_players

def allPlayersReady(ready_clients):
    index = 0
    proceedOrNot = True

    for allClients in client_sockets:
           
        if(ready_clients[index] == False):


            for client in client_sockets:
                # send data to all clients
               
                #commented out until a solution for slowing down the rate of sending is found
                #client.send(str(f"Waiting on Player {index + 1} to ready up!\n").encode("utf8"))
                proceedOrNot = False
               
        index += 1
    return proceedOrNot


#Token functions------USE if needed-------------------------------------------------------------------------------
def send_data_to_client(client, data_type, data):
    # Encode String before sending
    if data_type == "String":
        print(f"SEND {data} string to Client {client.id}: {data}")
        client.socket.send(str(data).encode('utf8'))

    # Serialize Object before sending            
    elif data_type == "Object":
        print(f"SEND {data} object to Client {client.id}: {data}")
        data_object = pickle.dumps(data)
        client.socket.send(data_object)

def print_ACK(player, ACK):
    print(f"Received ACK from Player {player.id}: {ACK}")

def readyUp(ready_clients, PlayerNumber, client_sockets):
    ready_clients[PlayerNumber-1] = True
    client_sockets[PlayerNumber-1].send("Server Acknowlegdes Ready Up\n".encode("utf8"))

    return ready_clients


def hostChoice():
    pass


def voteHost():
    pass


def answer():
    pass


def buzzing():
    pass


#Token functions-------------------------------------------------------------------------------------

if __name__ == "__main__":
    # setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM = TCP
    server.bind((HOST, PORT))
    server.listen()


    # data structures to hold client sockets and message queue so main can communicate with listening threads and vice versa
    client_sockets = []
    client_addrs = []
    PlayerNumber = {}


    ready_clients = [False, False, False, False, False]
    message_queue = Queue() # locks are already built in to Queue class
    recieve_connections_thread = Recieve_Connection_Thread(server, message_queue)
    recieve_connections_thread.start()

    #### Lobby loop ------------------------------------------------------------------
    host_found = False
    all_ready = False
    while not (all_ready and host_found):
        #gets the message and its coresponding sender adderess
        message, addr = message_queue.get()    
        print(message)

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]

        #### Internal Lobby states and values
        current_state = "WAIT"
        host = None
        total_votes = 0

        #### application layer protocol for lobby (Parse Tokens)
        tokens = message.split('-')

        #### Handle Requests for Data from Sender
        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]

            # Send client's own Player ID
            if request == "my_id":
                send_data_to_client(client, data_type, sender_id)

            # Send List of online Player IDs
            elif request == "player_id_list":
                player_id_list = []
                for c in clients.values():
                    player_id_list.append(c.id)
                send_data_to_client(client, data_type, player_id_list)

            elif request == "all_players_list":
                all_players = get_all_players()
                send_data_to_client(client, data_type, all_players)

            # Send client's own Player object
            elif request == "my_player":
                p_object = client.player_data
                send_data_to_client(client, data_type, p_object)

            # elif request == "total_votes":
            #     all_players = get_all_players()
            #     total_votes = lobby_state.get_total_votes(all_players)
            #     send_data_to_client(client, data_type, total_votes)

            if request == "lobby_state":
                all_players = get_all_players()
                last_state = current_state
                current_state = lobby_state.get_state(all_players, last_state)
                
                if current_state == "FIND_HOST":
                    host = lobby_state.calculate_host(all_players)
                    # TODO: send host to all clients, wait for ACK from all clients
                    current_state = "HOST_FOUND"
                elif current_state == "START_GAME":
                    # TODO: break out of lobby loop and start game
                    # Tell all clients that they can start the game
                    pass

                send_data_to_client(client, data_type, current_state)
                    

        elif (tokens[0] == "Vote_Host"):
            vote_id = int(tokens[1])
            clients[vote_id].player_data.votes += 1
            clients[sender_id].player_data.already_voted = True


        # TODO: when all players have finished voting, calculate final Host_choice and send to client
        # then set Player(Host_Choice).isHost = True  


        elif (tokens[0] == "Ready_Up"):
            ready_Clients = readyUp(ready_clients, PlayerNumber[addr][0], client_sockets)

        elif (tokens[0] == "ACK"):
            data = tokens[1]
            print_ACK(client, data)
           
    #Token Parse------------------------------------------------------------------


        all_ready = allPlayersReady(ready_clients)
        # If all players are ready move on to the main game loop
        if all_ready == True:
 
            break

    # close ability to connect
    recieve_connections_thread.stop()
    recieve_connections_thread.join()


    # send info to clients that main game has started
    # ...


    # main game loop
    game_loop = True
    while game_loop:
        message, addr = message_queue.get()
        print(message)


         # application layer protocol for game loop (parse tokens)
         # ...


        tokens = message.split('-')


       #Token Parse------------------------------------------------------------------


        if (tokens[0] == "Buzzing"):
               pass


        elif (tokens[0] == "Host_Choice"):
            pass
        elif (tokens[0] == "Answer"):
            pass


        #Token Parse------------------------------------------------------------------