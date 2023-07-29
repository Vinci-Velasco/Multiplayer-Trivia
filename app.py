### App.py facillitates communication between Frontend, Client, and Server

import streamlit as st
from src import connect_to_server, lobby, game, scoreboard
import client
from src import player

HOST = "127.0.0.1"
PORT = 7070

#### Initialize game states
def init_game(s):
    # Request data from client
    my_id = int(client.req_data_string(s, "my_id"))
    player_ids = client.req_data_object(s, "player_id_list")

    # Create a dict of Player objects on client side
    players = {}
    for p_id in player_ids:
        p_id_int = int(p_id)
        if p_id_int == my_id:
            players[p_id_int] = player.Player(p_id_int, is_me = True)
        else:
            players[p_id_int] = player.Player(p_id_int)
    
    # Store values into Streamlit App
    st.session_state.my_id = my_id
    st.session_state.players = players
    st.session_state.player_ids = player_ids

def update_players(s, data):
    pass

def gui_demo():
    if 'server' not in st.session_state:
        connect_to_server.main()
    elif 'game_start' not in st.session_state:
        lobby.main()
    elif 'game_over' not in st.session_state:
        game.main()
    elif 'show_scoreboard' not in st.session_state:
        scoreboard.main()

def main():
    #### connect to server
    if 'server' not in st.session_state:
        connect_to_server.main()
    else:
        # init_game(st.session_state.my_socket)
        s = st.session_state.my_socket
        if 'game_start' not in st.session_state:
            if 'my_id' not in st.session_state:
                init_game(s)
            lobby.main()
            ## TODO: Add way to keep checking game state from server, may need an additional thread... D:



    # lobby.main()

if __name__ == '__main__':
    main()