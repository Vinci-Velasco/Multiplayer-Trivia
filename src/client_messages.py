# functions to parse incoming messages to the Client, load the Data, and update Streamlit's session state
import pickle
import streamlit as st
import client

## update a Player in the game
def update_player(update, player_data):
    players = st.session_state.players

    if update == "Connect": # add newly connected player to dict
        player = pickle.loads(player_data)
        id = player.id
        players[id] = player
    else: # update attributes only if player with this ID exists
        id = int(player_data)
        if id in players: 
            if update == "Disconnect":
                players[id].disconnected = True 
            elif update == "Already_Voted":
                if players[id].already_voted == False:
                    players[id].already_voted = True
                    st.session_state.total_votes += 1
            elif update == "Readied_Up":
                players[id].readied_up = True
                st.session_state.total_ready += 1
            elif update == "Is_Host":
                players[id].is_host = True
                if players[id].is_me:
                    st.session_state.im_host = True
                else:
                    st.session_state.im_host = False
            elif update == "Score":
                players[id].score += 1
            
            elif update == "Has_Lock":
                players[id].has_lock = True
                st.session_state.buzzer_locked = True
                st.session_state.buzzer_id = id
                
                if players[id].is_me:
                    st.session_state.my_buzzer = True


## Store incoming data into Streamlit session state
def update_data(label, data):
    if data == None or label == None:
        return

    if label == "my_id":
            my_id = int(data)
            st.session_state.my_id = my_id

            if 'players' in st.session_state:
                players = st.session_state.players
                if my_id in players:
                    my_player = players[my_id]
                    my_player.is_me = True
                    st.session_state.my_player = my_player

    elif label == "players_in_lobby":
        ## Data contains list of all Players in the lobby
        players = {}
        total_votes = 0
        total_ready = 0 
        players_in_lobby = pickle.loads(data)

        for p in players_in_lobby:
            p_id = int(p.id)
            
            my_id = -1
            if 'my_id' in st.session_state:
                my_id = st.session_state.my_id

            if p_id == my_id:
                p.is_me = True
                st.session_state.my_player = p
            
            if p.already_voted:
                total_votes += 1
            
            if p.readied_up:
                total_ready += 1

            players[p_id] = p

        st.session_state.total_votes = total_votes    
        st.session_state.total_ready = total_ready
        st.session_state.players = players 
        
    elif label == "lobby_state":
        update_lobby_state(data)
    
    elif label == "game_state":
        update_game_state(data)

    elif label == "host_id":
        if 'host_id' not in st.session_state:
            print("getting host ID")
            host_id = int(data)
            host_found = False
            players = st.session_state.players

            for p in players.values():
                p_id = int(p.id)

                if p_id == host_id:
                    p.is_host = True
                    st.session_state.host_player = p
                    print("found host")

                    if p.is_me:
                        st.session_state.im_host = True
                    else:
                        st.session_state.im_host = False

                    host_found = True
                    break
        
        if host_found == True:
            print("assigning host")
            st.session_state.host_id = host_id
            st.session_state.ready_up = True
            
## GAME LOOP DATA Loop --------------------------
    elif label == "Timeout":
        id = int(data)
        if st.session_state.buzzer_locked == True and st.session_state.buzzer_id == id:
            players = st.session_state.players

            # Remove lock from player
            players[id].has_lock == False
            st.session_state.buzzer_locked = False
            
            if players[id].is_me:
                st.session_state.my_buzzer = False
        
    elif label == "Question":
        question = pickle.loads(data)
        st.session_state.current_question = question
    elif label == "Buzzing":
        buzz_id = int(data)
        
        if buzz_id == st.session_state.my_id:
            st.session_state.my_turn = True


    else:
        print(f"Error in Game! received unrecognized Send_Data label: {label}")
    
def update_game_state(game_state):
    if game_state == "SENDING_QUESTION":
        ## If client has received a Question from the server already...
        if 'current_question' in st.session_state and st.session_state.current_question != None and st.session_state.my_player.received_question == False:
            # Send Question Confirmation to server
            st.session_state.my_player.received_question = True
            client.send_data_to_server(st.session_state.my_socket, "Received_Question", "")
    
    elif game_state == "WAITING_FOR_BUZZ":
        # this is the only time buzzer should be open
        st.session_state.answer_phase = False
        st.session_state.buzzer_locked = False
        st.session_state.buzzer_phase = True
    
    elif game_state == "SOMEONE_BUZZED":
        if st.session_state.buzzer_locked == True: 
            st.session_state.buzzer_phase = False
            st.session_state.answer_phase = True

    st.session_state.game_state = game_state


#### handle current Lobby State, e.g. if we are in Voting phase or Ready Up phase...
def update_lobby_state(lobby_state):
    print("... this should update...")
    if lobby_state == "WAIT":
        # wait until minimum amount of players are in lobby before starting the game
        pass

    elif lobby_state == "VOTE":
        # minimum players are in lobby, start voting phase
        if st.session_state.min_players == False:
            st.session_state.min_players = True
  
    elif lobby_state == "HOST_FOUND":
        if st.session_state.min_players == False:
            st.session_state.min_players = True
        if 'host_id' in st.session_state:
            st.session_state.ready_up = True 
    elif lobby_state == "READY_UP":
        if st.session_state.min_players == False:
            st.session_state.min_players = True

        if ('host_id' in st.session_state) and 'ready_up' not in st.session_state:
            st.session_state.ready_up = True

    elif lobby_state == "START_GAME":
        print("Start Game!")
        st.session_state.ready_up_over = True

    elif lobby_state == "SENDING_QUESTION":
        print("error, SENDING_QUESTION is being sent in lobby_state!")
        pass

    st.session_state.lobby_state = lobby_state


def update_host_client(label, data):
    if 'im_host' in st.session_state and st.session_state.im_host == True:
        if label == "player_answer":
            player_answer = str(data)
            st.session_state.player_answer = player_answer

    else:
        my_id = st.session_state.my_id
        print(f"error: host data sent to client {my_id}")