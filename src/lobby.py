import streamlit as st



def init():
    nplayers = st.session_state.num_players

    if 'i_voted' not in st.session_state:
        st.session_state.i_voted = False
    if 'host_votes' not in st.session_state:
        # TODO: get this from the server instead
        st.session_state.host_votes = nplayers * [0]
        st.session_state.all_votes = nplayers * [False]

    st.session_state['game_start'] = False
    st.session_state['host_id'] = None

def update():
    # TODO: add code to refresh lobby

    # refresh player online status
    # refresh number of votes
    # refresh when host is chosen


    st.write('aaaa')


# def voting_progress():
#     nplayers = st.session_state.num_players

#     nvotes = st.session_state.all_votes.count(True)
#     while st.session_state.host_id == None:
#         vote.write (f"Votes: {nvotes}/{nplayers}")

# def send_vote():
#     if st.session_state.i_voted == False:
#         st.session_state.i_voted = True

#     # TODO: send Vote_Host tokens to server


def list_players():
    player, player_status, vote = st.columns([0.5, 0.6, 1])

    player.write("**Players**")
    player_status.write("**Status**")
    vote.write("**Vote Host**")

    nplayers = st.session_state.num_players

    # initialize online players dictionary. e.g. online['p1'] = True
    # online = {}
    online = dict.fromkeys(range(1, nplayers))

    for p in range(1, nplayers+1):
        online[p] = st.session_state.online_players[p-1]

        if p-1 == st.session_state.my_id:
            player.write(f"Player {p} (You)")
        else:
            player.write(f"Player {p}")

        if online[p]:
            player_status.write("Ready!")
        else:
            player_status.write("Waiting for connection...")

        vote.button('Vote',  disabled=(not online[p]), key=f"vote{p}")

    # for p in range(0, nplayers):
    #     online["p{0}".format(p+1)] = st.session_state.online_players[p]
    #     player, status, vote  = st.columns([0.5,0.6,1,1])

    #     if online[f'{p}']

    #     player.write(f"Player {p+1}")
    #     status.write(f"{status}")

    # cols = st.columns(nplayers)
    # for i, x in enumerate(cols):
    #     x.selectbox(f"Input # {i}", [nplayers], key=i)
    

def test():
    st.write(st.session_state)

    if st.button('Say hello'):
        st.session_state.key = 'bug'
        st.write(st.session_state.key)
        st.experimental_rerun()
    else:
        st.write('Goodbye')

def main():
    st.title('Lobby')
    
    init()


    list_players()


if __name__ == '__main__':
    main()