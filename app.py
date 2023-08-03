import streamlit as st
from queue import Empty
from src import connect_to_server, lobby, game, scoreboard
import client

#### Initialize data upon first connection
def init_data(s):
    # parse data from client
    client.req_data_string(s, "my_id")
    client.req_data_object(s, "all_players")

    my_id = -1
    all_players = []
    total_votes = 0

    # player_ids = client.req_data_object(s, "player_id_list")

    # Create a dict of Players by ID
    players = {}
    for p in all_players:
        p_id = int(p.id)
        if p_id == my_id:
            p.is_me = True
        if p.already_voted:
            total_votes += 1

        players[p_id] = p
    
    # Store values into Streamlit App
    st.session_state.my_id = my_id
    st.session_state.players = players
    st.session_state.total_votes = total_votes
    st.session_state.lobby_state = "LOADING"
    # st.session_state.player_ids = player_ids

def main():
    #### connect to server
    if 'server' not in st.session_state:
        connect_to_server.main()

    #### initialize message queue listening thread
    elif 'message_queue' not in st.session_state:
        connect_to_server.init_message_queue()

    else:
        s = st.session_state.my_socket
        message = st.session_state.new_message

        if 'game_start' not in st.session_state:
            if 'my_id' not in st.session_state:
                init_data(s)
            lobby.main()

if __name__ == '__main__':
    if 'server_disconnect' not in st.session_state:
        main()
    else:
        st.error("server disconnected.")