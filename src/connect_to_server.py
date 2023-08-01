import streamlit as st
import time
import socket
from src.player import Player
import threading
from queue import Queue

#### Test connection by pinging the server
def test_connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.send("ping".encode('utf-8'))
        return s.recv(1024).decode('utf-8'), s
    except ConnectionRefusedError as e:
        return e, e.filename

def exit():
    time.sleep(1)
    st.experimental_rerun()

# def listening_thread(sock, addr, message_queue):
#     BUFFER_SIZE = 1024 # change size when needed
#     with sock:
#         while True:
#             message = sock.recv(BUFFER_SIZE).decode("utf8")
#             message_queue.put((message, addr))
    
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
            # Initialize message queue and start listening thread
            # st.session_state.message_queue = Queue()
            # thread = threading.Thread(
            #     target=listening_thread, args=(st.session_state.my_socket, (st.session_state.server, st.session_state.port), st.session_state.message_queue))
            # thread.start()
            
            print(st.session_state)
            exit()
        
if __name__ == '__main__':
    main()