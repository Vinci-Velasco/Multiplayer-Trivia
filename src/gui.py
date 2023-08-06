import streamlit as st
#### Draw UI components
# Called on each page update

def draw_lobby(cols, players, vote_callback, ready_callback):
    ## Draw columns and titles
    st.title('Lobby')
    c1, c2, c3, c4 = st.columns(4, gap="large")        
    cols = { 1: c1, 2: c2, 3: c3, 4: c4 }

    cols[1].subheader('Players')
    cols[2].subheader('Status')

    if 'min_players' in st.session_state:
        if 'ready_up' not in st.session_state:
            cols[3].subheader('Vote Host')
        else:
            cols[3].subheader("Ready Up")
        
    ## List each connected player
    for p in players.values():
        if p.is_me:
            cols[1].write(f"Player {p.id} (You)")
        else:
            cols[1].write(f"Player {p.id}")

        # Write player status
        with cols[2]:
            if p.disconnected == True:
                st.write("Disconnected")
            elif 'min_players' not in st.session_state:
                st.write("Waiting...")
            elif p.already_voted == False:
                st.write("Voting...")
            elif 'ready_up' not in st.session_state:
                st.write("Waiting for votes...")
            elif p.readied_up == False:
                st.write("Readying up...")
            else:
                st.write('Waiting for game to start...')

        ## Populate buttons
        if 'min_players' not in st.session_state:
            continue
        elif 'ready_up' not in st.session_state:
            # Vote buttons
            vote_id = p.id + 0
            cols[3].button(f'Vote P{p.id}',  disabled=(st.session_state.i_voted or p.disconnected), on_click=vote_callback, args=(vote_id,), key=f"vote_btn{p.id}")
        elif p.is_me:
            # Ready Up buttons
            cols[3].button('Ready', disabled=(st.session_state.im_ready or p.disconnected), on_click=ready_callback)

    ## Display current progress

    if 'min_players' not in st.session_state:
        cols[4].write("Waiting for more players to join...")
    elif 'ready_up' not in st.session_state:
        # Begin Vote phase
        num_players = len(players)
        total_votes = st.session_state.total_votes
        # if (total_votes <= num_players):
        cols[4].write(f"Votes: {total_votes}/{num_players}")
    else: 
        # Begin Ready Up phase
        num_players = len(players)
        total_ready = get_total_ready(players.values())
        if (total_ready <= num_players):
            cols[4].write(f"Ready: {total_ready}/{num_players}")

    return cols

def get_total_ready(player_list):
    total_ready = 0
    for p in player_list:
        if p.readied_up:
            total_ready += 1

    return total_ready