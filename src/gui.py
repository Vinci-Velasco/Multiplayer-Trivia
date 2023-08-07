import streamlit as st
import client
import time
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
        if p.is_me and ('host_id' in st.session_state) and p.is_host:
            cols[1].write(f"Player {p.id} (You, Host)")
        elif ('host_id' in st.session_state) and p.is_host:
            cols[1].write(f"Player {p.id} (Host)")
        elif p.is_me:
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
                st.write("Already voted...")
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
        # total_ready = get_total_ready(players.values())
        total_ready = st.session_state.total_ready
        if (total_ready <= num_players):
            cols[4].write(f"Ready: {total_ready}/{num_players}")

    return cols

def draw_game_title():
    if st.session_state.host_phase:
        st.title("Host is checking answer...")
    elif st.session_state.answer_phase:
        st.title('Your turn!') 

    if ('current_question' in st.session_state) and (st.session_state.current_question != None):
        question = st.session_state.current_question
        st.header(f"Q{question.id}. {question.question}")
    else:
        st.header("Loading question...")

def draw_game(buzzer_callback):
    global cols
    c1, c2, c3 = st.columns(3, gap="large")
    cols = { 1: c1, 2: c2, 3: c3}

    ## only show Buzzer button during Buzzer phase
    if st.session_state.buzzer_phase == True:
        cols[2].button('Buzzer', on_click=buzzer_callback, use_container_width=True)

    elif st.session_state.answer_phase == True:
        player_turn()
    elif st.session_state.host_phase == True:
        host_turn()
        # "You are the player, waiting for host to verify"

def draw_host_game():
    global cols
    c1, c2, c3 = st.columns(3, gap="large")
    cols = { 1: c1, 2: c2, 3: c3}

    if st.session_state.buzzer_phase == True:
        st.write("You are the host. This is the Buzzer phase.")
    elif st.session_state.answer_phase:
        st.subheader("You are the host, someone is answering")
    elif st.session_state.host_phase:
        host_turn()

def player_turn():
    # TODO: check if my_id = buzzer_holder
    if st.session_state.my_turn:
        input = cols[2].text_input("Type your answer here")
        if input:
            # check answer with host
            
            st.session_state.last_answer = input
            st.session_state.answer_phase = False
            st.session_state.host_phase = True
            client.send_data_to_server(st.session_state.my_socket, "Answer", input) 
            st.experimental_rerun()
    else:
        st.subheader("Someone buzzed before you! They are answering")
    
def host_turn():
    question = st.session_state.current_question
    st.subheader(f"Player wrote: \"{st.session_state.last_answer}\"") 
    if st.session_state.host_id == st.session_state.my_id:
        st.write(f"Correct Answer: {question.answer}") 
        c1, c2 = st.columns(2)
        correct = c1.button("✅ Correct", use_container_width=True)
        incorrect = c2.button("❌ Incorrect", use_container_width=True)
        # TODO: update player scores
        if correct:
            st.success("Correct!")
            # can properly pass function instead of importing client
            client.send_data_to_server(st.session_state.my_socket, "Host_Choice", "y") 
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
            client.send_data_to_server(st.session_state.my_socket, "Host_Choice", "n")
            time.sleep(1)
            st.session_state.host_phase = False
            st.session_state.buzzer_phase = True
            st.experimental_rerun()