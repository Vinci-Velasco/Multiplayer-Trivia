import random
import time
import streamlit as st
from src.question_bank import *
from src import gui
import client

cols = {}

def init_game():
    st.session_state.buzzer_phase = True
    st.session_state.answer_phase = False
    st.session_state.host_phase = False

    st.session_state.my_turn = True

    if 'current_question' not in st.session_state:
        st.session_state.current_question = None


def buzzer_callback():
    st.session_state.buzzer_phase = False
    st.session_state.answer_phase = True

def main():
    if 'current_question' not in st.session_state:
        init_game()
    elif st.session_state.current_question == None:
        client.req_data_from_server(st.session_state.my_socket, "Question")
    else:
        gui.draw_game_title()
        if st.session_state.im_host == True:
            ### DRAW HOST UI
            gui.draw_host_game()
        else: 
            ### DRAW PLAYER UI
            gui.draw_game(buzzer_callback)

if __name__ == '__main__':
    main()