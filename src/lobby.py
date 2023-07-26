import streamlit as st
from src.player import Player

players = {}
cols = {}

def init(post_init=False):
    if not post_init: # TODO: receive from server
        st.session_state.i_voted = False
        st.session_state.im_ready = False
        st.session_state.total_votes = 0
        st.session_state.host_id = None

    st.session_state.game_start = False

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

def update_players():
    global players
    player_list = st.session_state.player_list
    players = player_list

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
    nplayers = len(players)
    total_votes = st.session_state.total_votes

    if (total_votes <= nplayers):
        cols[4].write (f"Votes: {total_votes}/{nplayers}")
    else:
        find_host()

def vote_callback():
    # testing
    st.session_state.total_votes += 1

def list_players():
    for p in players:
        if p.is_me:
            cols[1].write(f"Player {p.id} (You)")
        else:
            cols[1].write(f"Player {p.id}")

        if p.voted == False:
            cols[2].write("Voting...")
        else:
            cols[2].write('Waiting...')

        if 'ready_up' not in st.session_state:
            cols[3].button('Vote',  disabled=(st.session_state.i_voted), on_click=vote_callback, key=f"vote_btn{p.id}")

def main():
    st.title('Lobby')
    if 'total_votes' not in st.session_state:
        init()
    
    init_cols()
    update_players()
    list_players()

    if 'ready_up' not in st.session_state:
        vote_counter()
    else:
        ready_up()

    st.write(st.session_state)

if __name__ == '__main__':
    main()