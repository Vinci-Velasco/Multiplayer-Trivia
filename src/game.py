import streamlit as st
from src.question_bank import *
from src import gui
import time
import client

cols = {}

def init_game():
    if 'current_question' not in st.session_state:
        client.req_data_from_server(st.session_state.my_socket, "Question")

    if "game_state" not in st.session_state:
        st.session_state.game_state = "INIT"

        st.session_state.buzzer_phase = False
        # TODO remove answer_phase because its logically the same as buzzer_locked tbh
        st.session_state.answer_phase = False
        st.session_state.host_phase = False
        st.session_state.player_answer = "Null"

        st.session_state.buzzer_locked = False
        st.session_state.buzzer_id = None
        st.session_state.my_buzzer = False

def buzzer_callback():
    if st.session_state.buzzer_phase == True:
        # Send buzz to server
        client.send_data_to_server(st.session_state.my_socket, "Buzzing", "")
        st.session_state.buzzer_phase = False

def main():
    if 'current_question' not in st.session_state or 'game_state' not in st.session_state:
        init_game()
    elif st.session_state.game_state == "INIT":
        client.req_data_from_server(st.session_state.my_socket, "game_state")
    else:
        # Start Game
        gui.draw_game_title()

        global cols
        if st.session_state.im_host == True: # DRAW HOST UI
            cols = gui.draw_host_game()
        else: 
            cols = gui.draw_game(buzzer_callback)

if __name__ == '__main__':
    main()