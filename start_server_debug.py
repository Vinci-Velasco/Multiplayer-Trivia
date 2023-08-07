#### Start the Streamlit application on a random port number, allowing for multiple instances of the client

import os
import socket

PORT = 7070
offset = 0
OFFSET_MAX = 10
while True:
    os.system(f"python server.py {PORT+offset}")
    offset = (offset + 1) % OFFSET_MAX