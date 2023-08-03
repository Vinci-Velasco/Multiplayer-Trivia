# functions to parse incoming messages to the Client, load the Data, and update Streamlit's session state
import pickle
import streamlit as st

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
            elif update == "Is_Host":
                players[id].is_host = True
            elif update == "Score":
                players[id].score += 1

## Store incoming data into Streamlit session state
def update_data(label, data):
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
        players = {}
        total_votes = 0
        total_ready = 0 
        players_in_lobby = pickle.loads(data)

        for p in players_in_lobby:
            p_id = int(p.id)
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
    else:
        print(f"Error! received unrecognized Send_Data label: {label}")

#### handle current Lobby State, e.g. if we are in Voting phase or Ready Up phase...
def update_lobby_state(lobby_state):
    if lobby_state == "WAIT":
        # wait until minimum amount of players are in lobby before starting the game
        # TODO: turn off minimum players for testing purposes :]
        st.session_state.min_players = True

    elif lobby_state == "VOTE":
        # change session state variables so that lobby.py shows voting
        # send ack
        pass
    elif lobby_state == "HOST_FOUND":
        # change session state variables so lobby.py shows who is the new host
        # send ack
        pass
    elif lobby_state == "READY_UP":
        st.session_state.ready_up = True
        # st.session_state.vote_over = True
        pass
    elif lobby_state == "START_GAME":
        # send ack
        pass

    st.session_state.lobby_state = lobby_state