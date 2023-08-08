import sys
import streamlit as st
from src import connect_to_server, lobby, game, scoreboard

def main():
    ## connect to server
    if 'server' not in st.session_state:
        connect_to_server.main()

    ## initialize message queue thread
    elif 'message_queue' not in st.session_state:
        connect_to_server.init_message_queue()

    else:
        ## display lobby
        if 'game_start' not in st.session_state:
            lobby.main()
        elif 'game_over' not in st.session_state:
            game.main()
        else:
            scoreboard.main()

if __name__ == '__main__':
    if 'server_disconnect' not in st.session_state:
        main()
    else:
        st.error("server disconnected.")
        sys.exit("server disconnected.")