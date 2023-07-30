import os
import socket

# find random port number by binding to port 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 0))
addr = s.getsockname()
s.close()

os.system(f"streamlit run app.py --server.port {addr[1]}")