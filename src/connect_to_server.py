import streamlit as st
import time
import socket
import traceback
from src.player import Player

#### Test connection
def test_connect(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        try:
            my_socket.connect((host, port))
        except ConnectionRefusedError as e:
           return e
        finally:
            my_socket.close()
        return "success"

def exit():
    time.sleep(1)
    st.experimental_rerun()
    
#### Connect to server from Streamlit
def main():
    st.title('CMPT371 Project: Multiplayer Trivia Game')
    server = st.text_input("Enter Server IP")
    port = st.text_input("Enter Port")

    if server and port: # check user input
        port_num = int(port)
        with st.spinner(text=f"Now connecting to {server}"):
            connection = test_connect(server, port_num)
            time.sleep(1)

        if not connection == "success":
            st.exception(connection)
        else:
            st.success('Connection OK')
            st.session_state.port = port_num
            st.session_state.server = server
            exit()
        
if __name__ == '__main__':
    main()