import streamlit as st
from src import connect_to_server, lobby, game, scoreboard
from client import * 

HOST = "127.0.0.1"
PORT = 7070

# def init():
#     # define initial session states
#     st.session_state['winner'] = None
#     st.session_state['host'] = None

# def init_game():
#     # TODO: get this info from the server. for now just hardcode self as Player 1
#     my_id = 1
#     p1 = Player(my_id, is_me=True)
#     st.session_state.min_players = 3
#     st.session_state.max_players = 5
    
#     st.session_state['my_id'] = my_id
#     st.session_state['player_list'] = [p1]


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

if __name__ == '__main__':
    main()