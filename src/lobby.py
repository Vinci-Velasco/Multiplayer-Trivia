import streamlit as st

online = {}
cols = []

def init(post_init=False):
    nplayers = st.session_state.num_players

    if not post_init: # TODO: receive from server
        st.session_state.i_voted = False
        st.session_state.votes_list = nplayers * [0]
        # alternative: voted = nplayers * [False]?
        st.session_state.nvotes = 0

    st.session_state.game_start = False
    st.session_state.host_id = None

    #### online players dictionary
    # e.g. online['p1'] = True
    online = dict.fromkeys(range(1, nplayers))

def update():
    # TODO: add code to refresh lobby
    # refresh player online status
    # refresh number of votes
    # refresh when host is chosen
    st.write('aaaa')


def show_votes(c4):
    nplayers = st.session_state.num_players
    # nvotes = st.session_state.votes_list.count(True)
    nvotes = st.session_state.nvotes
    if st.session_state.host_id == None:
        c4.write (f"Votes: {nvotes}/{nplayers}")

# def send_vote():
#     if st.session_state.i_voted == False:
#         st.session_state.i_voted = True

#     # TODO: send Vote_Host tokens to server


def list_players(c1, c2, c3):
    nplayers = st.session_state.num_players

    for p in range(1, nplayers+1):
        online[p] = st.session_state.online_players[p-1]

        if p-1 == st.session_state.my_id:
            c1.write(f"Player {p} (You)")
        else:
            c2.write(f"Player {p}")

        if online[p]:
            c3.write("Ready!")
        else:
            c3.write("Waiting for connection...")

        c3.button('Vote',  disabled=(not online[p]), on_click=vote_callback, key=f"vote{p}")

def vote_callback():
    # testing
    st.session_state.nvotes += 1



def main():
    st.title('Lobby')
    init()

    c1, c2, c3, c4 = st.columns(4, gap="large")

    c1.write("**Players**")
    c2.write("**Status**")

    list_players(c1, c2, c3)
    show_votes(c4)


if __name__ == '__main__':
    main()