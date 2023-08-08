import socket
import threading
import time
import pickle
import json
import random
import sys, os
from queue import Queue

from src import player
from src.question_bank import Question
from game import lobby_state, game_state

HOST = "127.0.0.1"
PORT = 7072

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
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((HOST, port))

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
        target.player_data.disconnected = True
        client_socket.close()

        # notify remaining clients of disconnected client
        send_player_update_to_all("Disconnect", target.id)

        print(f"...closing inactive listening thread for client {target.id}")
    if len(sys.argv) > 1:
        print("exit")
        os._exit(1)


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

def clear_received_question():
    for c in clients.values():
         c.player_data.received_question = False

    game.all_players_viewed = False

def get_playerid_who_has_lock():
    for c in clients.values():
        p = c.player_data
        if p.has_lock == True:
            return p.id

    return None

def try_to_grab_buzz_lock(sender_id, time_thread):

    for c in clients.values():
        p = c.player_data

        #if anyone else has the lock DO NOT GIVE THE CALLING SENDER THE LOCK
        if p.has_lock == True and (p.id != sender_id):
            print(f"Buzzing denied for player {sender_id}")
            return False

    clients[sender_id].player_data.has_lock = True
    # send_message_to_all("Send_Data", "Buzzing", sender_id)
    send_player_update_to_all("Has_Lock", sender_id)

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
    for client in clients.values():
        if client.player_data.is_host:
            return client

    return None

#Token functions-------------------------------------------------------------------------------------


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
            to_console = str(data)[:10] + "..."
            print(f"(send_message_to_all) sending to {c.id}")
            if sent == False:
                sent = True
        else:
            print(f"(send_message_to_all) skipped {c.id}")

    if sent: # Print to console if successful
        to_console = str(data)[:10] + "..."
        print("....sent message to all clients:" + " { " + f"header: {header}, label: {label}, data: {to_console}" + " }\n")


#### Send an update to all clients about a specific Player
def send_player_update_to_all(update, player_data, serialize=False):
    header = "Player_Update"
    label = update # e.g. Connect, Disconnect

    if serialize == True:
        data = pickle.dumps(player_data)
    else:
        data = player_data

    send_message_to_all(header, label, data)

def send_state_update(state_type, state_data, serialize=False, to_all=False, client=None):
    header = "State_Update"
    label = state_type #e.g. Lobby, Game

    if serialize == True:
        data = pickle.dumps(state_data)
    else:
        data = state_data
    if to_all == True:
        send_message_to_all(header, label, data)
    elif client != None:
        send_message_to_client(client, header, label, data)

#### Handle requests for server data, send back a response containing the requested data
def parse_data_req(client, request, send_to_all=False):
    data = None
    serialize = False

    ## LOBBY LOOP DATA REQUESTS
    if request == "my_id":
        data = client.id

    elif request == "players_in_lobby":
        data = get_all_players()
        serialize = True

    elif request == "my_player":
        data = client.player_data
        serialize = True

    elif request == "lobby_state":
        lobby.update_players(player_list=get_all_players())
        print("lobby_state: getting state")
        lobby_state = lobby.get_state()
        print(f"lobby_state: sending state to all -> {lobby_state}")
        send_state_update("Lobby", lobby_state, to_all=True)
        return 

    ## GAME LOOP DATA REQUESTS
    if request == "Question":
        current_question = game.current_question

        if current_question != None:
            data = current_question
            serialize = True
            print("parse_data_request(Question):")

            global current_state
            if current_state != "SENDING_QUESTION":
                current_state = game.update_state("SENDING_QUESTION")
                send_state_update("Game", current_state, to_all=False, client=client)

        else:
            return

    elif request == "game_state":
        game.update_players(player_list=get_all_players())
        print("game_state: getting state")
        game_state = game.get_state()
        print(f"game_state: sending state to all -> {game_state}")
        send_state_update("Game", game_state, to_all=True)
        return 
    
    # Serialize data if needed
    if serialize == True:
        data = pickle.dumps(data)

    if send_to_all == True:
        send_message_to_all("Send_Data", request, data)
    else:
        send_message_to_client(client, "Send_Data", request, data)

def send_Host_To_All_Clients(host):
    send_message_to_all("Send_Data", "host_id", host.id)

def send_Start_Game_To_All_Clients():
    send_message_to_all("Send_Data", "lobby_state", "START_GAME")

def add_host_vote(client, vote_id):
    clients[vote_id].player_data.votes += 1
    clients[client.id].player_data.already_voted = True
    # update all clients that this client has voted
    send_player_update_to_all("Already_Voted", client.id)

# Send answer from player to host so the host can confirm if the answer is correct. Returns True if it went through, False otherwise
def send_answer_to_host(sender_id, event, answer):
    # ensure if the person who sent the answer token actually has the lock
    if sender_id != get_playerid_who_has_lock():
        print(f"Answer from {sender_id} rejected")
        return False
    
    # send answer to host
    host_client = get_host()

    print (f"Sending answer from {sender_id} to host {host_client.id}: {answer}\n")

    send_message_to_client(host_client, "Host_Verify", "player_answer", answer)

    # stop timer thread
    event.set()
    return True

# gets next question from question bank
def get_next_question(question_bank):
    # select rand question
    num_of_questions = len(question_bank["questions"])
    rand_num = random.randint(0, num_of_questions-1)
    selected_question = question_bank["questions"][rand_num]

    q = Question(selected_question["id"], selected_question["question"], selected_question["answer"])

    # avoid repeat questions
    question_bank["questions"].remove(selected_question)


    question = selected_question["question"]
    print(f"(get_next_question) Q: {question}")

    return q


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(sys.argv[1])
        port = int(sys.argv[1])
    # setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM = TCP
    server.bind((HOST, port))
    server.listen()
    print(f'Port is: {port}')

    # data structures to hold client sockets and message queue so main can communicate with listening threads and vice versa
    client_sockets = []
    client_addrs = []
    PlayerNumber = {}
    question_bank = load_question_bank()

    message_queue = Queue() # locks are already built in to Queue class
    recieve_connections_thread = Recieve_Connection_Thread(server, message_queue)
    recieve_connections_thread.start()

#### Lobby Loop ==========================================================================================

    #### Internal Lobby states and values
    lobby_loop = True
    host = None
    lobby = lobby_state.Lobby(player_list=get_all_players())

    while lobby_loop:
        # gets the message and its coresponding sender adderess
        message, addr = message_queue.get()
       
        # Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]
        print(f"Recieved message from {sender_id} @ {addr}: {message}\n")

        #Token Parse------------------------------------------------------------------

        tokens = message.split('-')

        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]
            parse_data_req(client, request)

        elif (tokens[0] == "Vote_Host"):
            vote_id = int(tokens[1])
            add_host_vote(client, vote_id)

        elif (tokens[0] == "Ready_Up"):
            clients[sender_id].player_data.readied_up = True
            send_player_update_to_all("Readied_Up", client.id)
        
        #### Update internal Lobby State
        lobby.update_players(player_list=get_all_players())
        current_state = lobby.get_state()
        
        # Additionally calculate host and broadcast to all clients
        if current_state == "FIND_HOST":
            if lobby.host_found() == False:
                host = lobby.calculate_host()
                clients[int(host.id)].player_data.is_host = True

            send_Host_To_All_Clients(host)
            current_state = lobby.update_state("HOST_FOUND")

        # current_state = lobby.get_state()
        if lobby.state_changed() and lobby.last_state != "WAIT":
            send_state_update("Lobby", current_state, to_all=True)

        if(current_state == "START_GAME"):
            break

    # close ability to connect
   
    recieve_connections_thread.stop()
    recieve_connections_thread.join()

    # send info to clients that main game has started
    send_Start_Game_To_All_Clients()

    # set up the timer thread for buzzing
    event = threading.Event()
    time_thread = threading.Thread(target=buzz_timer, args=(message_queue,))

#### Game Loop ==========================================================================================
    game_loop = True
    host_voted = False
    answer_came = False
    give_player_point = False
    new_question = False

    # Initialize Game object that represents the internal Game state
    if host != None:
        game = game_state.Game(host, player_list=get_all_players())
        current_state = game.current_state
        # initialize first question
        game.current_question = get_next_question(question_bank)
    else:
        game = None
        print("ERROR starting new Game: host not found")

    while game_loop:

        # # End Game when no more questions left
        # if len(question_bank) == 0:
        #     game.update_state("END_GAME")
        #     break

        message, addr = message_queue.get()

        #enter if the answer timer ran out and someone actually buzzed in
        if message == "Timeout" and get_playerid_who_has_lock() is not None:

            lock_id = get_playerid_who_has_lock()

            # Timeout all clients, remove lock for players[lock_id]
            send_message_to_all("Send_Data", "Timeout", lock_id)

            clients[lock_id].player_data.has_lock = False

            # return to buzzer state
            print("Back to buzzer state!")
            current_state = game.update_state("WAITING_FOR_BUZZ")

            send_state_update("Game", current_state, to_all=True)

            event = threading.Event()
            time_thread = threading.Thread(target=buzz_timer, args=(message_queue,))

            continue # needed because addr does not exist from message_queue.get() from the timer thread.

        if current_state == "WAITING_FOR_BUZZ":
            if game.all_players_viewed == True:
                clear_received_question()
                # send_player_update_to_all("Clear_Received", sender_id)

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]
        print(f"Recieved message from {sender_id} @ {addr}: {message}\n")

        #Token Parse------------------------------------------------------------------
        tokens = message.split('-')

        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]
            
            if request != "lobby_state":
                parse_data_req(client, request)

             # elif current_state == "GOT_HOST_CHOICE":

            #     #give_player_point variable is changed by the host_choice function which Tony is working on
            #     if(give_player_point == False):
            #         new_question = False
            #         give_player_point = False
            #         host_voted = False
            #         answer_came = False

            #         index = 1

            #         #goes through all players and takes away lock from player who buzzed without giving them a point
            #         #because host said their answer was wrong
            #         for p in all_players:

            #             if clients[index].player_data.has_lock == True:
            #                 clients[index].player_data.has_lock = False

            #             index += 1


            #         current_state = "WAITING_FOR_BUZZ"

            #         print("------AFTER THE HOST HAS CHOSEN (should all be false)---------------\n")
            #         print((f"#1: {all_players[0].has_lock}\n"))
            #         print((f"#2: {all_players[1].has_lock}\n"))
            #         print((f"#3: {all_players[2].has_lock}\n"))
            #         print("=====================\n")

            #     else:

            #         index = 1
            #         #goes through all players and takes away lock from player who buzzed but also give them a point
            #         for p in all_players:

            #             if clients[index].player_data.has_lock == True:
            #                 clients[index].player_data.has_lock == False
            #                 give_player_point = False
            #                 host_voted = False
            #                 answer_came = False
            #                 new_question = True
            #                 clients[index].player_data.increaseScore()
            #             index += 1

            #         #once a player gets the question right the server moves on to sending the next question
            #         current_state = "SENDING_QUESTION"

            #         #if someone has more than 5 points the the game ends
            #         if(game_state.has_someone_won(all_players)):
            #             current_state = "GAME_OVER"

            # elif current_state == "GAME_OVER":
            #     pass
            #     #TODO: send everyone a message telling each client the game is over
            #     #TODO: send everyoen the all_players list so each client can find out each persons score
            #     #TODO: might send everyone which player id won

            # elif current_state == "ENDING_GAME":

            #     #TODO: start shutting down threads
            #     break


            # send_message_to_client(client, "Send_Data", "game_state", current_state)

            #     # send_data_to_client(client, data_type, current_state)


        elif (tokens[0] == "Buzzing"):
           #whoever gets the lock set their player.has_lock to true once the GOT_HOST_CHOICE is over
           try_to_grab_buzz_lock(sender_id, time_thread)

        elif (tokens[0] == "Host_Choice"):
            choice = tokens[1]
            buzzer_id = get_playerid_who_has_lock()

            # Check if player who has lock exists
            if buzzer_id == None:
                print("ERROR in Host_Choice: no player has the buzzer")
                break

            if choice == "Y":
                # Update Player's score
                clients[buzzer_id].player_data.increaseScore()
                print(f"(Host_Choice) player {buzzer_id} gets 1 point")

                # Remove Player's lock
                clients[buzzer_id].player_data.has_lock = False

                # Update state to get new question on next loop
                current_state = game.update_state("GOT_HOST_CHOICE")
                game.next_question = True

                # Notify all clients about score update and Host_Choice
                send_player_update_to_all("Score", buzzer_id)
                send_message_to_all("Send_Data", "Host_Choice", "Y")
                send_state_update("Game", current_state, to_all=True)
                
            elif choice == "N":
                # Remove Player's lock
                clients[buzzer_id].player_data.has_lock = False
                
                # Update state
                current_state = game.update_state("GOT_HOST_CHOICE")

                send_message_to_all("Send_Data", "Host_Choice", "N")
                send_state_update("Game", current_state, to_all=True)

            else:
                print("(Host_Choice) error, unrecognized input")
                
        elif (tokens[0] == "Answer"):
            answer_str = str(tokens[1])

            current_state = game.update_state("WAITING_FOR_HOSTS_CHOICE")
            send_state_update("Game", current_state, to_all=True)

            # send answer to host
            answer_came = send_answer_to_host(sender_id, event, answer_str)

            # re-create thread instance (needed to start a new timer thread again for the future)
            if answer_came:
                time_thread = threading.Thread(target=buzz_timer, args=(message_queue,))

                answer_came = False
            
        elif (tokens[0] == "Received_Question"):
            # Confirmation that Sender has received the question
            clients[sender_id].player_data.received_question = True
        
        #### Update internal Game State
        if current_state != game.current_state: # state was changed manually
            current_state = game.update_state(current_state)
            print("game loop, current_state != game.current_state:")
            send_state_update("Game", current_state, to_all=True)

        else:
            game.update_players(player_list=get_all_players())
            current_state = game.get_state()

            if game.state_changed() == True:
                print("game_loop, state_changed() = True: ")
                send_state_update("Game", current_state, to_all=True)

        ## Handle special game state cases
        if game.next_question == True:
            # Check if no more questions in question bank
            if question_bank:
                game.current_question = get_next_question(question_bank)

                current_state = game.update_state("SENDING_QUESTION")

                game.next_question = False
            else:
                current_state = game.update_state("END_GAME")
                send_state_update("Game", "END_GAME", to_all=True)
                break

        elif(current_state == "END_GAME"):
            break
    
    ## TODO: at the end of gameloop, send all clients final copy of the player list for scoreboard