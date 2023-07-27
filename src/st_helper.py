import streamlit as st
# get session state
def state(key):
    return st.session_state[key]

def update():
    # TODO: add code to refresh lobby
    # refresh player online status
    # refresh number of votes
    # refresh when host is chosen
    st.write('aaaa')

# def send_vote():
#     if st.session_state.i_voted == False:
#         st.session_state.i_voted = True

#     # TODO: send Vote_Host tokens to server