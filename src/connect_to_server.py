#### Establishes socket connection to Server, initializes listening thread and message queue

import streamlit as st
import time
import socket
import threading
from queue import Queue
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

from client import listening_thread

#### Test connection by pinging the server
def test_connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.send("ping".encode('utf-8'))
        return s.recv(1024).decode('utf-8'), s
    except ConnectionRefusedError as e:
        return e, "Could not connect to server. Check inputs and make sure server.py is running."

def init_message_queue():
    # Add queue to Streamlit's session state, so it can be accessed throughout the application instance
    st.session_state.new_message = None
    st.session_state.num_messages = 0
    st.session_state.message_queue = Queue()

    s = st.session_state.my_socket

    t = threading.Thread(
    target=listening_thread, args=(s, st.session_state.message_queue))

    # Add thread to Streamlit's application context
    ctx = get_script_run_ctx()
    add_script_run_ctx(thread=t, ctx=ctx)

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

        if connection[0] == ConnectionRefusedError:
            st.error(connection[1])
        elif not connection[0] == "pong":
            st.exception(connection[0])
        else:
            st.success('Connection OK')
            st.session_state.port = port_num
            st.session_state.server = server
            st.session_state.my_socket = connection[1]

            exit()
        
if __name__ == '__main__':
    main()