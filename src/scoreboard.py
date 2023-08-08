import streamlit as st

def main():
    st.title("Scoreboard")
    c1, c2 = st.columns(2, gap="large")
    c1.subheader('Player')
    c2.subheader('Score')

    players = st.session_state.players

    for p in players.values():
        c1.write(f"Player {p.id}")
        if p.is_host:
            c2.write(f"<HOST>")
        else:
            c2.write(f"{p.score}")

    st.balloons()

if __name__ == '__main__':
    main()