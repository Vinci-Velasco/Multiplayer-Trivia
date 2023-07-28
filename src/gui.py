import streamlit as st
#### Draw UI components
# Called on each page update
def draw_lobby(cols, players, vote_callback, ready_callback):
    st.title('Lobby')
    c1, c2, c3, c4 = st.columns(4, gap="large")        
    cols = { 1: c1, 2: c2, 3: c3, 4: c4 }

    cols[1].subheader('Players')
    cols[2].subheader('Status')

    if 'ready_up' not in st.session_state:
        cols[3].subheader('Vote Host')
    else:
        cols[3].subheader("Ready Up")

    # List each connected
    for p in players:
        if p.is_me:
            cols[1].write(f"Player {p.id} (You)")
        else:
            cols[1].write(f"Player {p.id}")

        if p.voted == False:
            cols[2].write("Voting...")
        else:
            cols[2].write('Waiting...')

        if 'ready_up' not in st.session_state:
            cols[3].button('Vote',  disabled=(st.session_state.i_voted), on_click=vote_callback, key=f"vote_btn{p.id}")
        elif p.is_me:
            cols[3].button('Ready', on_click=ready_callback)