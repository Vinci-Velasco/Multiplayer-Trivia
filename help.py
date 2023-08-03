import threading
import streamlit as st
import time
import queue


q = queue.Queue()


def test_run():
    for x in range(1, 100):
        time.sleep(1)
        val = x
        multiply = val * 10        
        q.put((val, multiply))


is_exit_target_if_main_exits = True
threading.Thread(
    target=test_run,
    daemon=is_exit_target_if_main_exits).start()

# dashboard title
st.title("Streamlit Learning")

# creating a single-element container.
placeholder = st.empty()

# Exit loop if we will not receive data within timeoutsec.
timeoutsec = 30

# Simulate data from test_run() in placeholder.
while True:
    try:
        val, multiply = q.get(block=True, timeout=timeoutsec)
    except queue.Empty:
        break  # exit loop
    else:
        with placeholder.container():
            col1, col2 = st.columns(2)
            col1.metric(label="Current Value", value=val)
            col2.metric(label="Multiply by 10 ", value=multiply)
            q.task_done()