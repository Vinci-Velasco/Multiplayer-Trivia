import streamlit as st
from .gui import draw_lobby
from .player import Player

players = {}
cols = {}

## 'Public' methods for controlling Lobby State
def start_game():
    st.session_state.game_start = True
    st.experimental_rerun()

def init(post_init=False):
    if not post_init: # TODO: receive from server
        st.session_state.i_voted = False
        st.session_state.im_ready = False
        st.session_state.total_votes = 0
        st.session_state.total_ready = 0
        st.session_state.host_id = None
        
def vote_callback():
    # testing
    st.session_state.total_votes += 1

def ready_callback():
    st.session_state.total_ready += 1

#### Call server to update internal player states
def update_players():
    global players
    players = st.session_state.players

def find_host():
    # TODO: get host from server
    test_host = 1
    st.session_state.host_id = 1
    if 'vote_over' not in st.session_state:
        st.session_state.vote_over = True
        st.experimental_rerun()

def main():
    if 'total_votes' not in st.session_state:
        init()

    ## Update Session State
    update_players()

    ## Draw GUI
    global cols
    draw_lobby(cols, players, vote_callback, ready_callback, find_host)

    if 'ready_up_over' in st.session_state:
        start_game()

if __name__ == '__main__':
    main()