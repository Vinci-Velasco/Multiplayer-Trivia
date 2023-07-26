import streamlit as st
import time
from src.player import Player

def init_game():
    # TODO: get this info from the server. for now just hardcode self as Player 1
    my_id = 1
    p1 = Player(my_id, is_me=True)
    st.session_state.min_players = 3
    st.session_state.max_players = 5
    
    st.session_state['my_id'] = my_id
    st.session_state['player_list'] = [p1]

def connect(address):
    # TODO make this connect to server.py, check if valid connection
    if address=="valid":
        return True
    else:
        return False

def main():
    st.title('CMPT371 Project: Multiplayer Trivia Game')
    server = st.text_input("Enter Server IP")
    port = st.text_input("Enter Port")

    # TODO: CHANGE TO 'AND' WHEN READY
    if server or port:
        with st.spinner(text=f"Now connecting to {server}"):
            time.sleep(1)
            
        st.success('Connection OK')
        init_game()
        time.sleep(1)
        st.session_state.port = port
        st.session_state.server = server
        st.experimental_rerun()

if __name__ == '__main__':
    main()