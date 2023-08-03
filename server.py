import socket
import threading
import time
import pickle
import json
import random
from queue import Queue

from src import player
from src.question_bank import Question
from game import lobby_state, game_state

HOST = "127.0.0.1"
PORT = 7070

clients = {} # key: id - value: Client 


# Thread that deals with listening to clients
def listening_thread(client_socket, addr, message_queue):
    BUFFER_SIZE = 1024 # change size when needed

    with client_socket:
        while True:
            try:
                recv = client_socket.recv(BUFFER_SIZE)
                if not recv: # terminate thread if socket is inactive
                    disconnect_client(client_socket)
                    break
                message = recv.decode("utf8")
            except ConnectionResetError:
                disconnect_client(client_socket)
                break
            else:
                # receive a ping
                if message == "ping":
                    print("....got ping, sent pong")
                    client_socket.send("pong".encode('utf-8'))
                # add message to message queue
                else:
                    for m in message.split("\n"):
                        if m != "":
                            message_queue.put((m, addr))
                    print(f"Recieved message from {addr}: {message}\n")
         
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

           # Create a new Client and associated Player, add to global dict
            global clients
            client_id = connections
            p = player.Player(client_id)
            c = Client(client_id, client_socket, addr, p)
            clients[client_id] = c

            PlayerNumber[addr] =  client_id, client_socket

            # Notify all clients about the new connection (except this one)
            send_message_to_all("Player_Update", "Connect", pickle.dumps(p), except_id=client_id)

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
        # client_sockets.remove(client_socket)
        # client_addrs.remove(target.addr)
        # del PlayerNumber[target.addr]
        # del clients[target.id]
        target.player_data.disconnected = True
        client_socket.close()

        # notify remaining clients of disconnected client
        send_player_update_to_all("Disconnect", target.id)

        print(f"...closing inactive listening thread for client {target.id}")

# Returns a list of Players from all connected clients
def get_all_players():
    all_players = []
    for c in clients.values():
        all_players.append(c.player_data)

    return all_players


def givePoint(client_id):
    client = clients[client_id]
    players_data = client.player_data
    players_data.increaseScore()


def viewPlayerScore(client_id):
    client = clients[client_id]


    players_data = client.player_data
    print(players_data.getScore())


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

def received_question_confirmation(sender_id):
    clients[sender_id].player_data.received_question = True


def clear_received_question():

    all_players = get_all_players()

    index = 1
    for p in all_players:

         clients[index].player_data.received_question = False
         index += 1


def get_playerid_who_has_lock():
    for p in all_players:
        if p.has_lock == True:
            return p.id

    return None

def try_to_grab_buzz_lock(sender_id, time_thread):

    for p in all_players:

        #if anyone else has the lock DO NOT GIVE THE CALLING SENDER THE LOCK
        if(p.has_lock == True and p.id != clients[sender_id].player_data.id):
            return False

    clients[sender_id].player_data.has_lock = True

    time_thread.start()

# Thread that handles the timer when a person has buzzed in
def buzz_timer(message_queue):
    TIMER = 10

    # thread is no longer needed when answer is recieved and terminates normally
    if event.wait(TIMER):
        return

    # no answer recived, so timeout message sent to message queue to communicate to the main thread
    else:
        print("Timeout occurred")
        message_queue.put(("Timeout", ""))

# loads questions from JSON file and returns a dict
def load_question_bank():
    with open("./src/test_questions.json", "r") as file:
        return json.load(file)

# Returns who the host is if they have been selected, None otherwise
def get_host():
    for client in clients:
        if client.player_data.is_host:
            return client

    return None

#Token functions-------------------------------------------------------------------------------------

## TODO: Deprecated, don't use this
def send_data_to_client(client, data_type, data):
    # if client disconnected, don't do anything
    if client.socket.fileno() == -1:
        return
    
    # Encode String before sending
    if data_type == "String":
        print(f"....sending string to Client {client.id}: {data}")
        client.socket.send(str(data).encode('utf8'))

    elif data_type == "Object":
        print(f"....sending Object to Client {client.id}: {data}")
        data_object = pickle.dumps(data)
        client.socket.send(data_object)

#### Send message to client with header and label that describes the data
def send_message_to_client(client, header, label, data):
    message = {"header": header, "label": label, "data": data}
    client.socket.sendall(pickle.dumps(message))

    to_console = str(data)[:10] + "..."
    print(f"....sending message to Client {client.id}:" + " { " + f"header: {header}, label: {label}, data: {to_console}" + " }\n")


#### Send message to all clients except except_id
def send_message_to_all(header, label, data, except_id=-1):
    message = {"header": header, "label":label, "data":data}
    sent = False

    for c in clients.values():
        if c.id != except_id and c.player_data.disconnected == False:
       
            c.socket.sendall(pickle.dumps(message))
            if sent == False:
                sent == True

    if sent:
        to_console = str(data)[:10] + "..."
        print("....sending message to all clients:" + " { " + f"header: {header}, label: {label}, data: {to_console}" + " }\n")

#### Send an update to all clients about a specific Player
def send_player_update_to_all(update, player_data, serialize=False):
    header = "Player_Update"
    label = update # e.g. Connect, Disconnect

    if serialize == True:
        data = pickle.dumps(player_data)
    else:
        data = player_data

    send_message_to_all(header, label, data)

#### Handle requests for server data, send back a response containing the requested data
def parse_data_req(client, current_state, request, send_to_all=False):
    data = None
    serialize = False

    if request == "my_id":
        data = client.id

    elif request == "players_in_lobby":
        data = get_all_players()
        serialize = True

    elif request == "my_player":
        data = client.player_data
        serialize = True

    elif request == "lobby_state":
            all_players = get_all_players()
            last_state = current_state
            current_state = lobby_state.get_state(all_players, last_state)
            
            if current_state == "FIND_HOST":
                host = lobby_state.calculate_host(all_players)
                clients[host.id].player_data.is_host = True
                current_state = "HOST_FOUND"
             
                send_Host_To_All_Clients(host)
            elif current_state == "START_GAME":
                send_Start_Game_To_All_Clients()

                #if you send both of these together then the messages are received as one
                #send_data_to_client(client, data_type, current_state)

            data = current_state
          
    
    # Serialize data if needed
    if serialize == True:
        data = pickle.dumps(data)
    
    if send_to_all == True: 
        send_message_to_all("Send_Data", request, data) 
    else:
        send_message_to_client(client, "Send_Data", request, data)

    return current_state

def send_Host_To_All_Clients(host):

    send_message_to_all("Send_Data", "host_id", host.id)

def send_Start_Game_To_All_Clients():
    # TODO: change this to proper client message format eventually, i'm assuming this is for testing tho so i wont touch it
    for client in clients.values():
        client.socket.send(f"Start_Game-NA".encode('utf8'))

def hostChoice():
    pass

def add_host_vote(client, vote_id):
    clients[vote_id].player_data.votes += 1
    clients[client.id].player_data.already_voted = True
    # update all clients that this client has voted
    send_player_update_to_all("Already_Voted", client.id)

def voteHost():
    pass


# Send answer from player to host so the host can confirm if the answer is correct. Returns True if it went through, False otherwise
def answer(sender_id, event, message):
    # ensure if the person who sent the answer token actually has the lock
    if sender_id != get_playerid_who_has_lock():
        return False

    # send answer to host
    host_client = get_host()

    send_message_to_client(host_client, "Host_Verify", "player_answer", message)

    # send_data_to_client(host_client, "String", message)

    # stop timer thread
    event.set()
    return True

# Sends question from question bank to all clients
def send_question(question_bank):
    # select rand question
    num_of_questions = len(question_bank["questions"])
    rand_num = random.randint(0, num_of_questions-1)
    selected_question = question_bank["questions"][rand_num]

    q = Question(selected_question["id"], selected_question["question"], selected_question["answer"])

    # serialize and send to all
    q_data = pickle.dumps(q)
    send_message_to_all("Send_Data", "Question", q_data)

    # avoid repeat questions
    question_bank["questions"].remove(selected_question)


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
    question_bank = load_question_bank()


    ready_clients = [False, False, False, False, False]
    message_queue = Queue() # locks are already built in to Queue class
    recieve_connections_thread = Recieve_Connection_Thread(server, message_queue)
    recieve_connections_thread.start()

    # #### Lobby loop ------------------------------------------------------------------
    # host_found = False
    # all_ready = False
    # while not (all_ready and host_found):
    #     #gets the message and its coresponding sender adderess
    #     message, addr = message_queue.get()
    #     print(message)

    #### Lobby loop ------------------------------------------------------------------
    host_found = False
    all_ready = False
    #### Internal Lobby states and values
    host = None
    current_state = "WAIT"
    while not (all_ready and host_found):
        #gets the message and its coresponding sender adderess
        message, addr = message_queue.get()

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]

        #### Internal Lobby states and values
        total_votes = 0

        #### application layer protocol for lobby (Parse Tokens)
        tokens = message.split('-')

        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]
            current_state = parse_data_req(client, current_state, request)

        elif (tokens[0] == "Vote_Host"):
            vote_id = int(tokens[1])
            add_host_vote(client, vote_id)

        elif (tokens[0] == "Ready_Up"):
            clients[sender_id].player_data.readied_up = True

        if(current_state == "START_GAME"):
            break

    #Token Parse------------------------------------------------------------------

    # close ability to connect
    time.sleep(10)
    recieve_connections_thread.stop()
    recieve_connections_thread.join()

    # send info to clients that main game has started
    # ...

    # set up the timer thread for buzzing
    event = threading.Event()
    time_thread = threading.Thread(target=buzz_timer, args=(message_queue,))

   #Game Loop==========================================================================================
    # main game loop
    game_loop = True
    host_voted = False
    answer_came = False
    give_player_point = False
    current_state = "SENDING_QUESTION"
    while game_loop:

        # no more questions left
        if len(question_bank) == 0:
            break

        #send_question(question_bank)
        message, addr = message_queue.get()
        print(message)

        #enter if the answer timer ran out and someone actually buzzed in
        if message == "Timeout" and get_playerid_who_has_lock() is not None:
            buzz_lock = None

            # TODO: didnt change this to the new send_message_to_client yet cus idk what the purpose is
            for client_id in clients:
                send_data_to_client(clients[client_id], "String", "Timeout")

            #player who has lock loses it 
            clients[get_playerid_who_has_lock()].player_data.has_lock = False

            #we go back to buzzing stage to so others can get a chance to buzz
            print("Back to buzz!")
            current_state = "WAITING_FOR_BUZZ"

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]

        #### application layer protocol for lobby (Parse Tokens)
        tokens = message.split('-')


        #### Handle Requests for Data from Sender
        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]

            if request != "game_state":
                parse_data_req(client, current_state, request)
            # TODO: separate game_state parser after testing is done
            else:
                all_players = get_all_players()

                #PRINTING FOR TESTING - REMOVE IF NEEDED
                print("------Who HAS the lock (for testing)---------------\n")
                print((f"#1: {all_players[0].has_lock}\n"))
                print((f"#2: {all_players[1].has_lock}\n"))
                print((f"#3: {all_players[2].has_lock}\n"))
                print("=====================\n")
                last_state = current_state
                current_state = game_state.get_state(all_players, last_state)


                if current_state == "SENDING_QUESTION":
                    pass
                    #TODO: Send latest question to all clients

                elif current_state == "WAITING_FOR_BUZZ":

                    #this sets everyone's recieved_question variable back to false
                    clear_received_question()


                elif current_state == "WAITING_FOR_ANSWER":

                    #remove this when timer stuff gets added

                    if(answer_came):
                        current_state = "GOT_ANSWER"
                        answer_came = False
                    else:
                        current_state = "WAITING_FOR_ANSWER"


                elif current_state == "WAITING_FOR_HOSTS_CHOICE":

                    #host_voted gets updated when a host_vote token is parsed
                    if(host_voted == False):
                        current_state = "WAITING_FOR_HOSTS_CHOICE"
                    else:
                        current_state = "GOT_HOST_CHOICE"
                        host_voted = False

                elif current_state == "GOT_HOST_CHOICE":

                    #give_player_point variable is changed by the host_choice function which Tony is working on
                    if(give_player_point == False):
                        give_player_point = False
                        host_voted = False
                        answer_came = False

                        index = 1

                        #goes through all players and takes away lock from player who buzzed without giving them a point
                        #because host said their answer was wrong
                        for p in all_players:

                            if clients[index].player_data.has_lock == True:
                                clients[index].player_data.has_lock = False

                            index += 1


                        current_state = "WAITING_FOR_BUZZ"

                        print("------AFTER THE HOST HAS CHOSEN (should all be false)---------------\n")
                        print((f"#1: {all_players[0].has_lock}\n"))
                        print((f"#2: {all_players[1].has_lock}\n"))
                        print((f"#3: {all_players[2].has_lock}\n"))
                        print("=====================\n")

                    else:

                        index = 1
                        #goes through all players and takes away lock from player who buzzed but also give them a point
                        for p in all_players:

                            if clients[index].player_data.has_lock == True:
                                clients[index].player_data.has_lock == False
                                give_player_point = False
                                host_voted = False
                                answer_came = False
                                clients[index].player_data.increaseScore()
                            index += 1

                        #once a player gets the question right the server moves on to sending the next question
                        current_state = "SENDING_QUESTION"

                        #if someone has more than 5 points the the game ends
                        if(game_state.has_someone_won(all_players)):
                            current_state = "GAME_OVER"

                elif current_state == "GAME_OVER":
                    pass
                    #TODO: send everyone a message telling each client the game is over
                    #TODO: send everyoen the all_players list so each client can find out each persons score
                    #TODO: might send everyone which player id won

                elif current_state == "ENDING_GAME":

                    #TODO: start shutting down threads
                    break


                send_message_to_client(client, "Send_Data", "game_state", current_state) 

                # send_data_to_client(client, data_type, current_state)



        elif (tokens[0] == "Buzzing"):

           #whoever gets the lock set their player.has_lock to true once the GOT_HOST_CHOICE is over
           try_to_grab_buzz_lock(sender_id, time_thread)

        elif (tokens[0] == "Host_Choice"):
           
            host_voted = True

            if(tokens[1] == "Y"):
               give_player_point = True
            else:
               give_player_point = False

        elif (tokens[0] == "Answer"):
            answer_came = answer(PlayerNumber[addr][0], event, tokens[1])

            # re-create thread instance (needed to start a new timer thread again for the future)
            if answer_came:
                time_thread = threading.Thread(target=buzz_timer, args=(message_queue,))

        elif (tokens[0] == "Received_Question"):

            #whoever sends this must have their player.received_question set to true and will be changed once the waiting for buzz state is entered
            received_question_confirmation(sender_id)
    

        #Token Parse------------------------------------------------------------------
