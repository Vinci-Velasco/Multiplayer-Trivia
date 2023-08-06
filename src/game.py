import random
import time
import streamlit as st
from src.question_bank import *
from src import gui

cols = {}

def init():
    if 'qb' not in st.session_state:
       st.session_state.qb = qb_from_json()

    # no more questions
    if len(st.session_state.qb) == 0:
        st.session_state.game_over = True
        st.experimental_rerun()

    # initialize question
    st.session_state.current_question = random.choice(st.session_state.qb)

   # TODO: ask server whose turn it is
    st.session_state.buzzer_phase = True
    st.session_state.answer_phase = False
    st.session_state.host_phase = False

    st.session_state.my_turn = True


def buzzer_callback():
    st.session_state.buzzer_phase = False
    st.session_state.answer_phase = True

def player_turn():
    # TODO: check if my_id = buzzer_holder
    input = cols[2].text_input("Type your answer here")
    if input:
        # check answer with host
        st.session_state.last_answer = input
        st.session_state.answer_phase = False
        st.session_state.host_phase = True
        st.experimental_rerun()
    
def host_turn():
    #### TODO: check if my_id = host_id
    question = st.session_state.current_question
    st.subheader(f"Player wrote: \"{st.session_state.last_answer}\"") 
    st.write(f"Correct Answer: {question.answer}") 
    c1, c2 = st.columns(2)
    correct = c1.button("✅ Correct", use_container_width=True)
    incorrect = c2.button("❌ Incorrect", use_container_width=True)

    # TODO: update player scores
    if correct:
        st.success("Correct!")
        time.sleep(1)
        st.session_state.host_phase = False
        st.session_state.buzzer_phase = True
        # remove correct question from question bank
        question = st.session_state.current_question
        st.session_state.qb.remove(question)
        del st.session_state['current_question']
        st.experimental_rerun()
    if incorrect:
        st.error("Wrong answer")
        time.sleep(1)
        st.session_state.host_phase = False
        st.session_state.buzzer_phase = True
        st.experimental_rerun()

def main():
    if 'current_question' not in st.session_state:
        init()
    
    if st.session_state.host_phase:
        st.title("Host is checking answer...")
    elif st.session_state.answer_phase:
        st.title('Your turn!') 

    question = st.session_state.current_question
    st.header(f"Q{question.id}. {question.question}")
    
    gui.draw_game(buzzer_callback))

if __name__ == '__main__':
    main()