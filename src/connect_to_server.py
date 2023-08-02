#### Establishes socket connection to Server, initializes listening thread and message queue
# update_queue() is run each time a new message arrives from the server

import streamlit as st
import time
import socket
import threading
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
            message = sock.recv(BUFFER_SIZE).decode("utf8")
        except ConnectionResetError as e:
            # connection to server was interrupted
            break
        else:
            message_queue.put((message))
            # Run update_queue() to update frontend when a new message arrives in queue
            update_queue()


#### Runs each time a new message arrives from the server
def update_queue():
    message_queue = st.session_state.message_queue

    if st.session_state.new_message == None:
        try:
            message = message_queue.get(block=False)
        except Queue.Empty:
            print("error, queue is empty")
        else:
            st.session_state.new_message = message

    # Refresh app + message queue every 5 seconds
    time.sleep(5)
    streamlit_loop.call_soon_threadsafe(notify)

def init_message_queue():
    queue = Queue()
    s = st.session_state.my_socket
    t = threading.Thread(
    target=listening_thread, args=(s, queue, update_queue))

    # Add thread to Streamlit's application context
    ctx = get_script_run_ctx()
    add_script_run_ctx(thread=t, ctx=ctx)

    # Make thread daemonic to exit on ctrl+c
    t.daemon = True
    t.start()

    # Add queue to Streamlit's session state, so it can be accessed throughout the application instance
    st.session_state.new_message = None
    st.session_state.num_messages = 0
    st.session_state.message_queue = queue

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