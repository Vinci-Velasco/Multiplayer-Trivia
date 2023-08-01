### App.py facillitates communication between Frontend, Client, and Server

import streamlit as st
from src import connect_to_server, lobby, game, scoreboard
import client
from src import player
import threading
from queue import Queue
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

HOST = "127.0.0.1"
PORT = 7070

#### Initialize data upon first connection
def init_data(s):
   pass 
    # message = message_queue.get()    
    # st.write(message)

    # # Request data from client
    # my_id = int(client.req_data_string(s, "my_id"))
    # all_players = client.req_data_object(s, "all_players_list")
    # total_votes = 0
    # # player_ids = client.req_data_object(s, "player_id_list")

    # # Create a dict of Players by ID
    # players = {}
    # for p in all_players:
    #     p_id = int(p.id)
    #     if p_id == my_id:
    #         p.is_me = True
    #     if p.already_voted:
    #         total_votes += 1

    #     players[p_id] = p
    
    # # Store values into Streamlit App
    # st.session_state.my_id = my_id
    # st.session_state.players = players
    # st.session_state.total_votes = total_votes
    # # st.session_state.player_ids = player_ids

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

def queue_callback():
    message_queue = st.session_state.message_queue
    message = message_queue.get()    
    print(f"received message in queue: {message}")
    st.write(f"received message in queue: {message}")

def main():
    #### connect to server
    if 'server' not in st.session_state:
        connect_to_server.main()
    else:
        s = st.session_state.my_socket

        if 'message_queue' not in st.session_state:
            queue = Queue()
            t = threading.Thread(
            target=client.listening_thread, args=(s, queue, queue_callback))
            ctx = get_script_run_ctx()
            add_script_run_ctx(thread=t, ctx=ctx)
            t.start()
            print("i started the thread pls respond")
            st.session_state.message_queue = queue
            st.experimental_rerun()
            # t = client.init_thread(s, st.session_state.message_queue, queue_callback)
        else:
            client.req_data_string(s, "my_id")



        # if 'game_start' not in st.session_state:
        #     if 'my_id' not in st.session_state:
        #         init_data(s)
        #     lobby_state = client.update_lobby(s)
        #     if lobby_state == "VOTE":
        #         pass
        #     lobby.main(lobby_state)
        #     ## TODO: Add way to keep checking game state from server, may need an additional thread... D:

if __name__ == '__main__':
    main()