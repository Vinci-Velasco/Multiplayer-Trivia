import streamlit as st
from client import send_data_to_server
import time
import asyncio
#### Draw UI components
# Called on each page update

def draw_lobby(cols, players, vote_callback, ready_callback):
    ## Draw columns and titles
    st.title('Lobby')
    c1, c2, c3, c4 = st.columns(4, gap="large")        
    cols = { 1: c1, 2: c2, 3: c3, 4: c4 }

    cols[1].subheader('Players')
    cols[2].subheader('Status')

    if st.session_state.min_players == True:
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
            elif st.session_state.min_players == False :
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
        if st.session_state.min_players == False:
            continue
        elif 'ready_up' not in st.session_state:
            # Vote buttons
            vote_id = p.id + 0
            cols[3].button(f'Vote P{p.id}',  disabled=(st.session_state.i_voted or p.disconnected), on_click=vote_callback, args=(vote_id,), key=f"vote_btn{p.id}")
        elif p.is_me:
            # Ready Up buttons
            cols[3].button('Ready', disabled=(st.session_state.im_ready or p.disconnected), on_click=ready_callback)

    ## Display current progress

    if st.session_state.min_players == False:
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
    if st.session_state.host_phase == True:
        st.title("Host is checking answer...")

    elif st.session_state.answer_phase:
        if st.session_state.buzzer_locked == True:
            if st.session_state.my_buzzer == True:
               
               time_left = 10
               if (st.session_state.question_timer != None):
                   time_left = st.session_state.question_timer - time.time() + 10.99
                   time_left = int(time_left)
               title = st.title(f"Your turn! Time Remaining: {time_left}")
            #    asyncio.create_task(watch(title, st.session_state.question_timer, st.session_state.timing_down))
            #    print("asdf")
            else:
               st.title(f"Player {st.session_state.buzzer_id} has the buzzer!")
        else:
            st.title("Someone buzzed!")

    if ('current_question' in st.session_state) and (st.session_state.current_question != None):
        question = st.session_state.current_question
        st.header(f"Q{question.id}. {question.question}")
    else:
        st.header("Loading question...")

async def watch(test, timer, running):
    print(st.session_state.question_timer)
    print(st.session_state.timing_down)
    if True:
        print("")
        st.session_state.timing_down = True
        print("b")
        running = True
        print(timer)
        while timer > 0:
            if "question_timer" not in st.session_state:
                break
            timer = st.session_state.question_timer
            # test.title(f"Your turn! Time Remaining: {timer}")
            r = await asyncio.sleep(1)
            if "question_timer" not in st.session_state:
                break
            st.session_state.question_timer -= 2
            print(st.session_state.question_timer)
        st.session_state.timing_down = False
        print("e")


def draw_game(buzzer_callback):
    global cols
    c1, c2, c3 = st.columns(3, gap="large")
    cols = { 1: c1, 2: c2, 3: c3}

    ## only show Buzzer button during Buzzer phase
    if st.session_state.buzzer_phase == True:
        cols[2].button('Buzzer', on_click=buzzer_callback, use_container_width=True)
    
    elif st.session_state.host_choice != None:
        if st.session_state.host_choice == "Y":
                st.toast("Correct answer!")
                time.sleep(0.5)
        elif st.session_state.host_choice == "N":
                st.toast("Wrong answer.")
                time.sleep(0.5)

        return
   
    ## Start Answer phase when some player has_lock
    elif st.session_state.answer_phase == True and st.session_state.buzzer_locked == True:
            buzzer_id = st.session_state.buzzer_id
            if buzzer_id == st.session_state.my_id:
                player_turn()
            else:
                st.write(f"Player {buzzer_id} has the buzzer. Waiting...")
            
    ## Start Host phase when host is verifying answer
    elif st.session_state.host_phase == True:
        if st.session_state.player_answer != "Null":
            st.info(f"Your answer: \"{st.session_state.player_answer}\"")

        st.write("Waiting for Host to verify answer...")
    
    else:
        with st.spinner("Loading..."):
            time.sleep(0.2)
    
def draw_host_game():
    global cols
    c1, c2, c3 = st.columns(3, gap="large")
    cols = { 1: c1, 2: c2, 3: c3}

    if st.session_state.buzzer_phase == True:
        st.write("You are the host.")
    elif st.session_state.host_choice != None:
        if st.session_state.host_choice == "Y":
                st.toast("Correct answer!")
                time.sleep(0.5)
        elif st.session_state.host_choice == "N":
                st.toast("Wrong answer.")
                time.sleep(0.5)

        return

    elif st.session_state.answer_phase == True and st.session_state.buzzer_locked == True:
        buzzer_id = st.session_state.buzzer_id
        st.write(f"You are the Host. Player {buzzer_id} has the buzzer. Waiting...")        

    elif st.session_state.host_phase == True:
        host_turn()
        
def player_turn():
    with cols[2]:
        input_container = st.empty()
        input_container.text_input("Type your answer here", key="answer_input")

    sent = False
    if st.session_state.answer_input != "" and sent == False:
        # Callback when player enters an answer
        answer = str(st.session_state.answer_input)
        st.session_state.player_answer = answer
        send_data_to_server(st.session_state.my_socket, "Answer", answer)
        sent = True
        # Clear input box
        input_container.empty()
    
def host_turn():
    question = st.session_state.current_question

    st.subheader(f"Player wrote: \"{st.session_state.player_answer}\"") 
    st.write(f"Correct Answer: {question.answer}") 

    # Draw Correct/Incorrect buttons
    c1, c2 = st.columns(2)
    correct = c1.button("✅ Correct", use_container_width=True)
    incorrect = c2.button("❌ Incorrect", use_container_width=True)
    # TODO: update player scores

    if correct:
        st.success("Correct!")
        send_data_to_server(st.session_state.my_socket, "Host_Choice", "Y") 
    
    if incorrect:
        st.error("Wrong answer")
        send_data_to_server(st.session_state.my_socket, "Host_Choice", "N")