import socket
import threading
import pickle
from queue import Queue
from src import player
from game import lobby_state

HOST = "127.0.0.1"
PORT = 7073

clients = {} # key: id - value: Client 

# Thread that deals with listening to clients
def listening_thread(client_socket, addr, message_queue):
    BUFFER_SIZE = 1024 # change size when needed

    with client_socket:
        while True:
            try:
                message = client_socket.recv(BUFFER_SIZE).decode("utf8")
            except ConnectionResetError:
                disconnect_client(client_socket)
                break
            else:
                # terminate listening thread when client socket is inactive
                if not message:
                    disconnect_client(client_socket)
                    break
            
                # receive a ping
                if message == "ping":
                    print("....got ping, sent pong")
                    client_socket.send("pong".encode('utf-8'))
                # add message to message queue
                else:
                    for m in message.split("\n"):
                        if m != "":
                            message_queue.put((m, addr))
                    print(f"Recieved message from {addr}: {message}")
         
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

           # Create a new Client and associated Player serialize, add to global dict
            global clients
            client_id = connections
            p = player.Player(client_id)
            c = Client(client_id, client_socket, addr, p)
            clients[client_id] = c

            PlayerNumber[addr] =  client_id, client_socket

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

def disconnect_client(client_socket):
    target = None
    for c in clients.values():
        if c.socket == client_socket:
            target = c
            break
    
    if target != None:
        client_sockets.remove(client_socket)
        client_addrs.remove(target.addr)
        del PlayerNumber[target.addr]
        # del clients[target.id]
        target.player_data.disconnected = True
        client_socket.close()
        print(f"...closing inactive listening thread for client {client.id}")

# Returns a list of all Player data from all connected clients
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

  #### Send/Parse Messages ------------------------------------------------------------------

#### Automatically format data before sending based on data_type
# TODO: LEGACY, needs to be redone
def send_data_to_client(client, data_type, data):
    # if client disconnected, don't do anything
    if client.socket.fileno() == -1:
        return
    
    # Encode String before sending
    if data_type == "String":
        print(f"....sending string to Client {client.id}: {data}")
        client.socket.send(str(data).encode('utf8'))

    # Serialize Object before sending            
    elif data_type == "Object":
        print(f"....sending serialize to Client {client.id}: {data}")
        data_object = pickle.dumps(data)
        client.socket.send(data_object)

#### Send message to client with header and label that describes the data
def send_message_to_client(client, header, label, data):
    message = {"header": header, "label": label, "data": data}
    client.socket.sendall(pickle.dumps(message))

    to_console = str(data)[:10] + "..."
    print(f"....sending message to Client {client.id}:" + " { " + f"header: {header}, label: {label}, data: {to_console}" + " }")


#### Send message to all clients
def send_message_to_all(header, label, data):
    message = {"header": header, "label":label, "data":data}
    for c in clients.values():
        c.socket.sendall(pickle.dumps(message))

    to_console = str(data)[:10] + "..."
    print("....sending message to all clients:" + " { " + f"header: {header}, label: {label}, data: {to_console}" + " }")

#### Handle requests for server data, send back a response containing the requested data
def parse_data_req(client, request, send_to_all=False):
    data = None
    serialize = False

    if request == "my_id":
        data = client.id

    elif request == "all_players":
        data = get_all_players()
        serialize = True

    elif request == "my_player":
        data = client.player_data
        serialize = True

    if request == "lobby_state":
        all_players = get_all_players()
        global current_state
        last_state = current_state
        current_state = lobby_state.get_state(all_players, last_state)
        
        if current_state == "FIND_HOST":
            host = lobby_state.calculate_host(all_players)
            current_state = "HOST_FOUND"
        elif current_state == "START_GAME":
            # Tell all clients that they can start the game
            pass
        
        data = current_state
    
    # Serialize data if needed
    if serialize == True:
        data = pickle.dumps(data)
    
    if send_to_all == True: 
        send_message_to_all("Send_Data", request, data) 
    else:
        send_message_to_client(client, "Send_Data", request, data)


#Token functions------ if needed-------------------------------------------------------------------------------

def readyUp(ready_clients, PlayerNumber, client_sockets):
    ready_clients[PlayerNumber-1] = True
    client_sockets[PlayerNumber-1].send("Server Acknowlegdes Ready Up\n".encode("utf8"))

    return ready_clients


def hostChoice():
    pass


def add_host_vote(client, vote_id):
    clients[vote_id].player_data.votes += 1
    clients[client.id].player_data.already_voted = True
    # update all clients
    parse_data_req(None, "all_players", send_to_all=True)

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

    #### Internal Lobby states and values
    host = None
    total_votes = 0
    while not (all_ready and host_found):
        #gets the message and its coresponding sender adderess
        message, addr = message_queue.get()    

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]

        #### application layer protocol for lobby (Parse Tokens)
        tokens = message.split('-')

        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]
            parse_data_req(client, request)
                    
        elif (tokens[0] == "Vote_Host"):
            vote_id = int(tokens[1])
            add_host_vote(client, vote_id)
            
        elif (tokens[0] == "Ready_Up"):
            ready_Clients = readyUp(ready_clients, PlayerNumber[addr][0], client_sockets)

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