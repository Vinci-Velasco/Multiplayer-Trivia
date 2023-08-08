import streamlit as st
from src.question_bank import *
from src import gui
import client

cols = {}

def end_game():
    st.session_state.game_over = True
    print("Game over!")
    st.experimental_rerun()

def init_game():
    if "game_state" not in st.session_state:
        st.session_state.game_state = "INIT"

    st.session_state.buzzer_phase = False
    st.session_state.answer_phase = False
    st.session_state.host_phase = False

    st.session_state.buzzer_locked = False
    st.session_state.buzzer_id = None
    st.session_state.my_buzzer = False
    st.session_state.question_timer = None
    st.session_state.timing_down = False

def buzzer_callback():
    if st.session_state.buzzer_phase == True:
        # Send buzz to server
        client.send_data_to_server(st.session_state.my_socket, "Buzzing", "")
        st.session_state.buzzer_phase = False

def main():
    if 'game_over' in st.session_state:
        end_game()
    elif 'game_state' not in st.session_state:
        init_game()
    elif st.session_state.game_state == "INIT":
        client.req_data_from_server(st.session_state.my_socket, "game_state")
    elif ('current_question' not in st.session_state or st.session_state.current_question == None) and st.session_state.my_player.received_question == False:
        st.session_state.player_answer = "Null"
        st.session_state.host_choice = None
        st.session_state.current_question = None
        client.req_data_from_server(st.session_state.my_socket, "Question")
    else:
        # Start Game
        gui.draw_game_title()

        if st.session_state.im_host == True: # DRAW HOST UI
            gui.draw_host_game()
        else: 
            gui.draw_game(buzzer_callback)
        
        if 'host_choice' in st.session_state and st.session_state.host_choice != None and 'game_over' not in st.session_state:
            st.session_state.current_question = None
            st.session_state.host_choice = None
            st.session_state.my_player.received_question = False
            init_game()
            st.experimental_rerun()

if __name__ == '__main__':
    main()