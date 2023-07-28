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
        

def vote_counter():
    nplayers = len(players)
    total_votes = st.session_state.total_votes

    if (total_votes <= nplayers):
        cols[4].write(f"Votes: {total_votes}/{nplayers}")
    else:
        find_host()

def vote_callback():
    # testing
    st.session_state.total_votes += 1

def ready_callback():
    st.session_state.total_ready += 1

def ready_up():
    nplayers = len(players)
    total_ready = st.session_state.total_ready
    if (total_ready <= nplayers):
        cols[4].write(f"Ready: {total_ready}/{nplayers}")
    else:
        # Start game
        start_game()

#### Call server to update internal states

def update_players():
    global players
    player_ids = st.session_state.player_ids
    players = player_ids

def find_host():
    # TODO: get host from server
    test_host = 1
    st.session_state.host_id = 1
    if 'ready_up' not in st.session_state:
        st.session_state.ready_up = False
        st.experimental_rerun()
    ready_up()

def main():
    if 'total_votes' not in st.session_state:
        init()

    ## Update Session State
    update_players()

    ## Draw GUI
    global cols
    draw_lobby(cols, players, vote_callback, ready_callback)

    if 'ready_up' not in st.session_state:
        vote_counter()
    else:
        ready_up()

if __name__ == '__main__':
    main()