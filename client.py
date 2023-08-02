import socket
import time
import pickle
import streamlit as st
from queue import Queue
from src.st_notifier import notify, streamlit_loop 

def listening_thread(sock, message_queue):
    BUFFER_SIZE = 1024
    while True:
        try:
            recv = sock.recv(BUFFER_SIZE)
            message = recv.decode("utf-8")
        except UnicodeDecodeError: # If decoding doesn't work, message is not a string. Deserialize with pickle
            message = pickle.loads(recv)
            to_console = message["header"] + "-" + message["label"]
            print(f"Received message from server: {to_console}")
            message_queue.put(message)
            update_queue(message_queue)
        else:
            print(f"Received message from server: {message}")
            for m in message.split("\n"):
                if m != "":
                    message_queue.put(m)
            update_queue(message_queue)
    
#### Runs each time a new message arrives from the server to update the front-end
def update_queue(message_queue):
    try:
        message = message_queue.get(block=False)
        print(message)
    except Queue.empty:
        print("error, queue is empty")
    else:
        try:
            # parse message as string
            parse_message_as_string(message)
        except AttributeError:
            # parse message with pickle
            parse_message(message)

    # Refresh app + message queue every 0.1 seconds
    time.sleep(.1)
    streamlit_loop.call_soon_threadsafe(notify)


def parse_message(message):
    if message["header"] == "Send_Data":
        label = message["label"]
        data = message["data"]

        if label == "my_id":
            my_id = int(data)
            st.session_state.my_id = my_id
        elif label == "all_players":
            players = {}
            total_votes = 0
            all_players = pickle.loads(data)
            for p in all_players:
                p_id = int(p.id)
                if p_id == st.session_state.my_id:
                    p.is_me = True
                if p.already_voted:
                    total_votes += 1

                players[p_id] = p
            st.session_state.players = players 
            st.session_state.total_votes = total_votes

# LEGACY, all messages coming in need to be deserialized
def parse_message_as_string(message):
    tokens = message.split('-')

    if tokens[0] == "Send_Data":
        label = tokens[2]
        data = tokens[3]

        if label == "my_id":
            my_id = int(data)
            st.session_state.my_id = my_id
        elif label == "all_players":
            print(data)
            all_players = pickle.loads(data.encode("utf-8"))
            st.session_state.all_players = all_players 
            print(all_players)
        elif label == "lobby_state":
            pass
            
        pass

#### handle current Lobby State, e.g. if we are in Voting phase or Ready Up phase...
def update_lobby_state(lobby_state):
    if lobby_state == "WAIT":
        # wait until minimum amount of players are in lobby before starting the game
        pass
    elif lobby_state == "VOTE":
        # change session state variables so that lobby.py shows voting
        # send ack
        pass
    elif lobby_state == "HOST_FOUND":
        # change session state variables so lobby.py shows who is the new host
        # send ack
        pass
    elif lobby_state == "READY_UP":
        # st.session_state.ready_up = True
        # st.session_state.vote_over = True
        # send ack
        pass
    elif lobby_state == "START_GAME":
        # send ack
        pass

#### Data Strings need to be decoded with utf8
# Deprecated
def req_data_string(s, string):
    s.send(f"Req_Data-String-{string}\n".encode('utf8'))

#### Data Objects need to be serialized/deserialized with pickle
# Deprecated
def req_data_object(s, object):
    BUFFER_SIZE = 1024
    s.send(f"Req_Data-Object-{object}\n".encode('utf8'))


def ready_up_test():
    HOST = "127.0.0.1"
    PORT = 7070
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.connect((HOST, PORT))

        index = 0
        while True:
            time.sleep(3)
            my_socket.send("hello".encode("utf8"))


            BUFFER_SIZE = 1024
    
            data = my_socket.recv(BUFFER_SIZE).decode("utf8")
            print(f"Recived: {data}")
        
            #on 5th loop client can choose to ready up (only here for testing change as needed)
            if(index == 5):
                userTestInput = input("would you like to ready up? ('y' or 'n'): ")

                if(userTestInput == "y"):
                    my_socket.send("Ready_Up-3-some type of data".encode("utf8"))


            index += 1


if __name__ == '__main__':
    ready_up_test()