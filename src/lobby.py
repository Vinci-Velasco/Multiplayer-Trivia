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

        if 'my_id' not in st.session_state:
            st.session_state.my_id = -1
        if 'players' not in st.session_state:
            st.session_state.players = {}
            st.session_state.total_votes = 0
            st.session_state.total_ready = 0
        else:
            st.session_state.i_voted = False
            st.session_state.im_ready = False
            st.session_state.host_id = None
            st.session_state.lobby_start = True

def vote_callback(id):
    s = st.session_state.my_socket
    s.send(f"Vote_Host-{id}".encode('utf8'))
    # st.session_state.i_voted = True

def ready_callback():
    st.session_state.total_ready += 1

def find_host():
    # TODO: get host from server
    test_host = 1
    # st.session_state.host_id = 1
    # if 'vote_over' not in st.session_state:
    #     # st.session_state.vote_over = True
    #     st.experimental_rerun()

def main():
    if 'lobby_start' not in st.session_state:
        init(st.session_state.my_socket)
    else:
        players = st.session_state.players
        st.session_state.i_voted = st.session_state.my_player.already_voted

        ## Draw GUI
        global cols
        draw_lobby(cols, players, vote_callback, ready_callback, find_host)

        if 'ready_up_over' in st.session_state:
            start_game()
        
        st.write(st.session_state)

if __name__ == '__main__':
    main()