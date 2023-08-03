import streamlit as st
from queue import Empty
from src import connect_to_server, lobby, game, scoreboard
import client

def main():
    #### connect to server
    if 'server' not in st.session_state:
        connect_to_server.main()

    #### initialize message queue listening thread
    elif 'message_queue' not in st.session_state:
        connect_to_server.init_message_queue()

    else:
        s = st.session_state.my_socket

        if 'game_start' not in st.session_state:
            lobby.main()

if __name__ == '__main__':
    if 'server_disconnect' not in st.session_state:
        main()
    else:
        st.error("server disconnected.")