import streamlit as st

from src import connect_to_server, lobby, game, scoreboard

def init():
    # define initial session states
    st.session_state['winner'] = None
    st.session_state['host'] = None

# note: use streamlit.empty to generate a container?  https://discuss.streamlit.io/t/display-a-text-variable-that-periodically-changing/11531

def main():
    init();

    if 'server' not in st.session_state:
        connect_to_server.main()
    elif 'lobby' not in st.session_state:
        lobby.main()
    elif 'game_over' not in st.session_state:
        game.main()
    else:
        scoreboard.main()

if __name__ == '__main__':
    main()