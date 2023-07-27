import os
import streamlit as st
from src.question_bank import *

question = None

def init():
    # TODO: server should handle question bank but hardcode here for now
    if 'qb' not in st.session_state:
       st.session_state.qb = qb_from_json()

    # initialize question
    if 'current_question' not in st.session_state:
        st.session_state.current_question = random.choice(st.session_state.qb)
        global question
        question = st.session_state.current_question
    
def buzzer():
    left_co, cent_co,last_co = st.columns(3, gap="large")
    with cent_co:
        st.button('Buzzer', use_container_width=True)


def main():
    st.title('Game')
    init()
    st.header(f"Q{question.id}. {question.question}")
    buzzer()


if __name__ == '__main__':
    main()