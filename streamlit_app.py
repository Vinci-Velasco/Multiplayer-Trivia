import streamlit as st

from src import connect_to_server, lobby

def init():
    # define initial session states
    st.session_state['winner'] = None
    st.session_state['host'] = None
    st.session_state['game_over'] = False

# note: use streamlit.empty to generate a container?  https://discuss.streamlit.io/t/display-a-text-variable-that-periodically-changing/11531

def main():
    if 'server' not in st.session_state:
        connect_to_server.main()
    elif 'lobby' not in st.session_state:
        lobby.main()

if __name__ == '__main__':
    main()