#### Establishes socket connection to Server, initializes listening thread and message queue
# update_queue() is run each time a new message arrives from the server

import streamlit as st
import time
import socket
import threading
import pickle
from queue import Queue
from src.st_notifier import notify, streamlit_loop 
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

#### Test connection by pinging the server
def test_connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.send("ping".encode('utf-8'))
        return s.recv(1024).decode('utf-8'), s
    except ConnectionRefusedError as e:
        return e, "Could not connect to server. Check inputs and make sure server.py is running."

def listening_thread(sock, message_queue, update_queue):
    BUFFER_SIZE = 1024 # change size when needed
    while True:
        try:
            # print("trying to receive")
            recv = sock.recv(BUFFER_SIZE)
            # print("got to receive")
            message = recv.decode("utf-8")
        except ConnectionResetError as e:
            # connection to server was interrupted
            break
        except UnicodeDecodeError as e:
            message = pickle.loads(recv)
            print(message)
            message_queue.put(message)
            update_queue()
        else:
            for m in message.split("\n"):
                if m != "":
                    message_queue.put(m)
            # Run update_queue() to update frontend when a new message arrives in queue
            update_queue()

#### Runs each time a new message arrives from the server
def update_queue():
    message_queue = st.session_state.message_queue
    try:
        message = message_queue.get(block=False)
        print(message)
    except Queue.Empty:
        print("error, queue is empty")
    else:
        try:
            parse_message(message)
        except AttributeError:
            parse_message_object(message)

    # Refresh app + message queue every 5 seconds
    time.sleep(.1)
    print("refresh")
    streamlit_loop.call_soon_threadsafe(notify)

def parse_message_object(message):

    if message["header"] == "Send_Data":
        request = message["request"]
        data = message["data"]

        if request == "my_id":
            my_id = int(data)
            st.session_state.my_id = my_id
        elif request == "all_players":
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
        elif request == "lobby_state":
            # parse_lobby_state(data)
            # meepy does this
            pass
            

def parse_message(message):
    tokens = message.split('-')

    if tokens[0] == "Send_Data":
        request = tokens[2]
        data = tokens[3]

        if request == "my_id":
            my_id = int(data)
            st.session_state.my_id = my_id
        elif request == "all_players":
            print(data)
            all_players = pickle.loads(data.encode("utf-8"))
            st.session_state.all_players = all_players 
            print(all_players)
        elif request == "lobby_state":
            # parse_lobby_state(data)
            # meepy does this
            pass
            
        pass

    elif tokens[0] == "Lobby_State":
        pass

#### handle current Lobby State, e.g. if we are in Voting phase or Ready Up phase...
def parse_lobby_state(lobby_state):
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
        st.session_state.ready_up = True
        st.session_state.vote_over = True
        # send ack
        pass
    elif lobby_state == "START_GAME":
        # send ack
        pass
    

def init_message_queue():
    queue = Queue()

    # Add queue to Streamlit's session state, so it can be accessed throughout the application instance
    st.session_state.new_message = None
    st.session_state.num_messages = 0
    st.session_state.message_queue = queue

    s = st.session_state.my_socket
    t = threading.Thread(
    target=listening_thread, args=(s, queue, update_queue))

    # Add thread to Streamlit's application context
    ctx = get_script_run_ctx()
    add_script_run_ctx(thread=t, ctx=ctx)

    # Make thread daemonic to exit on ctrl+c
    t.daemon = True
    t.start()

    st.experimental_rerun()

def exit():
    time.sleep(1)
    st.experimental_rerun()

#### Connect to server from Streamlit GUI
def main():
    st.title('CMPT371 Project: Multiplayer Trivia Game')
    server = st.text_input("Enter Server IP")
    port = st.text_input("Enter Port")

    if server and port: # check user input
        port_num = int(port)
        with st.spinner(text=f"Now connecting to {server}"):
            connection = test_connect(server, port_num)
            time.sleep(1)

        if not connection[0] == "pong":
            st.exception(connection[0])
        else:
            st.success('Connection OK')
            st.session_state.port = port_num
            st.session_state.server = server
            st.session_state.my_socket = connection[1]

            exit()
        
if __name__ == '__main__':
    main()