import streamlit as st
from src.player import Player

online = {}
cols = {}

MIN_PLAYERS = 3

def init(post_init=False):
    nplayers = st.session_state.num_players 

    if not post_init: # TODO: receive from server
        st.session_state.i_voted = False
        st.session_state.im_ready = False
        st.session_state.votes_per_player = nplayers * [0]
        st.session_state.total_votes = 0
        st.session_state.host_id = None

    st.session_state.game_start = False

    # e.g. online['p1'] = True
    online = dict.fromkeys(range(1, nplayers), False)

def init_cols():
    global cols
    c1, c2, c3, c4 = st.columns(4, gap="large")        
    cols = { 1: c1, 2: c2, 3: c3, 4: c4 }
    cols[1].write("**Players**")
    cols[2].write("**Status**")

    if 'ready_up' not in st.session_state:
        cols[3].write("**Vote Host**")
    else:
        cols[3].write("**Ready Up**")

def ready_up():
    cols[3].button('Ready')        

def find_host():
    # TODO: get host from server
    test_host = 1
    st.session_state.host_id = 1
    if 'ready_up' not in st.session_state:
        st.session_state.ready_up = False
        st.experimental_rerun()
    ready_up()

def vote_counter():
    nplayers = st.session_state.num_players
    total_votes = st.session_state.total_votes

    if (total_votes <= nplayers):
        cols[4].write (f"Votes: {total_votes}/{nplayers}")
    else:
        find_host()

def vote_callback():
    # testing
    st.session_state.total_votes += 1

def list_players():
    nplayers = st.session_state.num_players

    for p in range(1, nplayers+1):
        online[p] = st.session_state.online_players[p-1]

        if p == st.session_state.my_id:
            cols[1].write(f"Player {p} (You)")
        else:
            cols[1].write(f"Player {p}")

        if online[p]:
            cols[2].write("Ready!")
        else:
            cols[2].write("Waiting for connection...")

        if 'ready_up' not in st.session_state:
            cols[3].button('Vote',  disabled=(not online[p]), on_click=vote_callback, key=f"vote_btn{p}")

def main():
    st.title('Lobby')
    if 'total_votes' not in st.session_state:
        init()
    
    init_cols()
    list_players()

    if 'ready_up' not in st.session_state:
        vote_counter()
    else:
        ready_up()

    st.write(st.session_state)

if __name__ == '__main__':
    main()