import streamlit as st
#### Draw UI components
# Called on each page update

def draw_lobby(cols, players, vote_callback, ready_callback, find_host):
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
    for p in players.values():
        if p.is_me:
            cols[1].write(f"Player {p.id} (You)")
        else:
            cols[1].write(f"Player {p.id}")

        if p.already_voted == False:
            cols[2].write("Voting...")
        else:
            cols[2].write('Waiting...')

        if 'vote_over' not in st.session_state:
            cols[3].button(f'Vote P{p.id}',  disabled=(st.session_state.i_voted), on_click=(lambda: vote_callback(p.id)), key=f"vote_btn{p.id}")
        elif p.is_me:
            cols[3].button('Ready', on_click=ready_callback)

    if 'vote_over' not in st.session_state:
        nplayers = len(players)
        total_votes = st.session_state.total_votes

        if (total_votes <= nplayers):
            cols[4].write(f"Votes: {total_votes}/{nplayers}")
        else:
            find_host()
    else: ## Begin Ready Up phase after Vote Over
        nplayers = len(players)
        total_ready = st.session_state.total_ready
        if (total_ready <= nplayers):
            cols[4].write(f"Ready: {total_ready}/{nplayers}")
        else:
            st.session_state.ready_up_over = True

    return cols