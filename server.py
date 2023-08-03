import socket
import threading
import time
import pickle
import json
import random
from queue import Queue
from src import player
from src.question_bank import Question
from game import lobby_state
from game import game_state


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

                #client_socket.send("Server acknowledges your message\n".encode())


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

#Helper functions------------------------------------------------------------------------------------
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

#Helper functions------------------------------------------------------------------------------------



#Token functions-------------------------------------------------------------------------------------
def send_data_to_client(client, data_type, data):
    # Encode String before sending
    if data_type == "String":
        print(f"SEND {data} string to Client {client.id}: {data}")
        client.socket.send(str(data).encode('utf8'))

    elif data_type == "Object":
        print(f"SEND {data} object to Client {client.id}: {data}")
        data_object = pickle.dumps(data)
        client.socket.send(data_object)


def send_Host_To_All_Clients(host):

    for client in clients.values():
        client.socket.send(f"Host_Number-{host.id}".encode('utf8'))


def send_Start_Game_To_All_Clients():

    for client in clients.values():
        client.socket.send(f"Start_Game-NA".encode('utf8'))


def print_ACK(player, ACK):
    print(f"Received ACK from Player {player.id}: {ACK}")


def hostChoice():
    pass

def voteHost():
    pass


# Send answer from player to host so the host can confirm if the answer is correct. Returns True if it went through, False otherwise
def answer(sender_id, event, message):
    # ensure if the person who sent the answer token actually has the lock
    if sender_id != get_playerid_who_has_lock():
        return False

    # send answer to host
    host_client = get_host()
    send_data_to_client(host_client, "String", message)

    # stop timer thread
    event.set()
    return True

# Sends question from question bank to all clients
def send_question(question_bank):
    # select rand question
    num_of_questions = len(question_bank["questions"])
    rand_num = random.randint(0, num_of_questions-1)
    selected_question = question_bank["questions"][rand_num]

    question_obj = Question(selected_question["id"], selected_question["question"], selected_question["answer"])

    # serialize and send
    global clients
    for client_id in clients:
        send_data_to_client(clients[client_id], "Object", question_obj)

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
    current_state = "WAIT"
    host = None
    while not (all_ready and host_found):
        #gets the message and its coresponding sender adderess
        message, addr = message_queue.get()
        print(message)

    #     #### Handle Requests for Data from Sender
    #     if (tokens[0] == "Req_Data"):
    #         data_type = tokens[1]
    #         request = tokens[2]

        #### Information about the Sender
        sender_id = PlayerNumber[addr][0]
        client = clients[sender_id]


        #### Internal Lobby states and values
        total_votes = 0


        #### application layer protocol for lobby (Parse Tokens)
        tokens = message.split('-')

    #         elif request == "all_players_list":
    #             all_players = get_all_players()
    #             send_data_to_client(client, data_type, all_players)

        #### Handle Requests for Data from Sender
        if (tokens[0] == "Req_Data"):
            data_type = tokens[1]
            request = tokens[2]

    #         # elif request == "total_votes":
    #         #     all_players = get_all_players()
    #         #     total_votes = lobby_state.get_total_votes(all_players)
    #         #     send_data_to_client(client, data_type, total_votes)

            # Send client's own Player ID
            if request == "my_id":
                send_data_to_client(client, data_type, sender_id)

    #             if current_state == "FIND_HOST":
    #                 host = lobby_state.calculate_host(all_players)
    #                 # TODO: send host to all clients, wait for ACK from all clients
    #                 current_state = "HOST_FOUND"
    #             elif current_state == "START_GAME":
    #                 # TODO: break out of lobby loop and start game
    #                 # Tell all clients that they can start the game
    #                 pass

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

                    clients[host.id].player_data.is_host = True

                    send_Host_To_All_Clients(host)

                    current_state = "HOST_FOUND"
                elif current_state == "START_GAME":

                    send_Start_Game_To_All_Clients()

                    #if you send both of these together then the messages are received as one
                    #send_data_to_client(client, data_type, current_state)
                    break

                send_data_to_client(client, data_type, current_state)


        elif (tokens[0] == "Vote_Host"):
            vote_id = int(tokens[1])
            clients[vote_id].player_data.votes += 1
            clients[sender_id].player_data.already_voted = True

        # TODO: when all players have finished voting, calculate final Host_choice and send to client
        # then set Player(Host_Choice).isHost = True

        elif (tokens[0] == "Ready_Up"):

            clients[sender_id].player_data.readied_up = True

        elif (tokens[0] == "ACK"):
            data = tokens[1]
            print_ACK(client, data)

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

        send_question(question_bank)
        message, addr = message_queue.get()
        print(message)

        if message == "Timeout" and get_playerid_who_has_lock() is not None:
            buzz_lock = None

            for client_id in clients:
                send_data_to_client(clients[client_id], "String", "Timeout")

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

            if request == "game_state":
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
                    current_state = "GOT_ANSWER"


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

                        inex = 1
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


                send_data_to_client(client, data_type, current_state)



        elif (tokens[0] == "Buzzing"):

           #whoever gets the lock set their player.has_lock to true once the GOT_HOST_CHOICE is over
           try_to_grab_buzz_lock(sender_id, time_thread)

        elif (tokens[0] == "Host_Choice"):

           host_voted = True
           #TODO:call/create the hostChoice funciton which actually asks the host if the answer is right or wrong
           #the hostChoice function should return true or false which gets stored into give_player_point
           #ie. give_player_point = hostChoice()
           pass

        elif (tokens[0] == "Answer"):
            answer_came = answer(PlayerNumber[addr][0], event, tokens[1])

            # re-create thread instance (needed to start a new timer thread again for the future)
            if answer_came:
                time_thread = threading.Thread(target=buzz_timer, args=(message_queue,))

        elif (tokens[0] == "Received_Question"):

            #whoever sends this must have their player.received_question set to true and will be changed once the waiting for buzz state is entered
            received_question_confirmation(sender_id)


        elif (tokens[0] == "ACK"):
            data = tokens[1]

            print_ACK(client, data)

        #Token Parse------------------------------------------------------------------
