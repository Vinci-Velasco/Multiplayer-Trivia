import streamlit as st
import client
from .gui import draw_lobby

cols = {}

## 'Public' methods for controlling Lobby State
def start_game():
    st.session_state.game_start = True
    st.experimental_rerun()

#### Initialize data upon first connection
def init(s):
    with st.spinner("loading lobby..."):
        client.req_data_from_server(s, "my_id")
        client.req_data_from_server(s, "players_in_lobby")
        client.req_data_from_server(s, "lobby_state")

        if 'my_id' not in st.session_state:
            st.session_state.my_id = -1
        if 'players' not in st.session_state:
            st.session_state.players = {}
            st.session_state.total_votes = 0
            st.session_state.total_ready = 0
        if "lobby_state" not in st.session_state:
            st.session_state.lobby_state = "WAIT"
        else:
            st.session_state.i_voted = False
            st.session_state.im_ready = False
            st.session_state.lobby_start = True

# Send Vote to server when vote button is clicked
def vote_callback(vote_id):
    header = "Vote_Host"
    data = vote_id
    client.send_data_to_server(st.session_state.my_socket, header, data)

# Send Ready to server when ready button is clicked
def ready_callback():
    header = "Ready_Up" 
    data = ""
    client.send_data_to_server(st.session_state.my_socket, header, data)
    # st.session_state.total_ready += 1

def main():
    if 'lobby_start' not in st.session_state:
        init(st.session_state.my_socket)
    else:
        players = st.session_state.players
        lobby_state = st.session_state.lobby_state

        if not st.session_state.i_voted:
            st.session_state.i_voted = st.session_state.my_player.already_voted

        ## Draw GUI
        global cols
        draw_lobby(cols, players, vote_callback, ready_callback)

        if 'ready_up_over' in st.session_state:
            start_game()
        
        st.write(st.session_state)

if __name__ == '__main__':
    main()