import random
import time
import streamlit as st
from src.question_bank import *
from src import gui
import client

cols = {}

def init_game():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None

    st.session_state.buzzer_phase = True
    st.session_state.answer_phase = False
    st.session_state.host_phase = False

    st.session_state.my_turn = True


def buzzer_callback():
    st.session_state.buzzer_phase = False
    st.session_state.answer_phase = True

def main():
    if 'current_question' not in st.session_state:
        init_game()
    elif st.session_state.current_question == None:
        client.req_data_from_server(st.session_state.my_socket, "Question")
    else:
        if st.session_state.host_phase:
            st.title("Host is checking answer...")
        elif st.session_state.answer_phase:
            st.title('Your turn!') 

        question = st.session_state.current_question
        st.header(f"Q{question.id}. {question.question}")
        
        gui.draw_game(buzzer_callback)

if __name__ == '__main__':
    main()