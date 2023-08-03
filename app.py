import streamlit as st
from queue import Empty
from src import connect_to_server, lobby, game, scoreboard
import client

#### Initialize data upon first connection
def init_lobby(s):
    client.req_data_from_server(s, "my_id")
    client.req_data_from_server(s, "players_in_lobby")

    st.spinner("loading lobby...")

    if 'my_id' not in st.session_state:
        st.session_state.my_id = -1

    if 'players' not in st.session_state:
        st.session_state.players = {}
        st.session_state.total_votes = 0
    else:
        st.session_state.lobby_start = True

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
            if 'lobby_start' not in st.session_state:
                init_lobby(s)
            else:
                lobby.main()

if __name__ == '__main__':
    if 'server_disconnect' not in st.session_state:
        main()
    else:
        st.error("server disconnected.")