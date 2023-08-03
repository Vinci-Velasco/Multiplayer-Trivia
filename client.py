import socket
import time
import pickle
import streamlit as st
from queue import Empty
from src.st_notifier import notify, streamlit_loop 
from src import client_messages


def listening_thread(sock, message_queue):
    BUFFER_SIZE = 1024
    while True:
        try:
            recv = sock.recv(BUFFER_SIZE)
            if not recv:
                server_disconnect()
                break
            message = recv.decode("utf-8")
        except UnicodeDecodeError: # If decoding doesn't work, message is not a string. Deserialize with pickle
            message = pickle.loads(recv)
            to_console = "{ header: " + message['header'] + ", label: " + message['label'] + ", data: " + str(message['data'])[:10] + "... }"
            print(f"Received message from server: {to_console}\n")
            message_queue.put(message)
            update_queue(message_queue)
        except Exception:
            break
        else:
            print(f"Received a string from server: {message}\n")
            for m in message.split("\n"):
                if m != "":
                    message_queue.put(m)
            update_queue(message_queue)
    
#### Runs each time a new message arrives from the server to update the front-end
def update_queue(message_queue):
    try:
        message = message_queue.get(block=False)
    except Empty as e:
        raise Exception('error, queue is empty. did server disconnect?') from e
    else:
        parse_message(message)

        # Refresh app + message queue every 0.1 seconds
        time.sleep(.1)
        streamlit_loop.call_soon_threadsafe(notify)

# Close and delete socket when Server disconnects
def server_disconnect():
    st.session_state['server_disconnect'] = True
    st.session_state.my_socket.close()
    del st.session_state.my_socket
    time.sleep(.1)
    streamlit_loop.call_soon_threadsafe(notify)

def req_data_from_server(s, request):
    message = f"Req_Data-String-{request}\n" 
    print(f"...sending message to server: {message}\n")
    s.sendall(message.encode('utf8'))

def send_data_to_server(s, header, data):
    message = f"{header}-{data}\n"
    print(f"...sending message to server: {message}\n")
    s.sendall(message.encode('utf8'))

#### Parse incoming messages in queue
def parse_message(message):
    if message["header"] == "Send_Data":
        label = message["label"]
        data = message["data"]
        client_messages.update_data(label, data)

    elif message['header'] == "Player_Update":
        update = message['label']
        player_data = message['data']

        if 'players' in st.session_state:
            client_messages.update_player(update, player_data)
    
    elif message['header'] == "State_Update":
        label = message['label']
        state_data = message['data']

        if label == "Lobby" and 'lobby_start' in st.session_state:
            client_messages.update_lobby_state(state_data)
        elif label == "Game" and 'game_start' in st.session_state:
            client_messages.update_game_state(state_data)

#### Data Strings need to be decoded with utf8
def req_data_string(s, string):
    message = f"Req_Data-String-{string}\n" 
    print(f"...sending message to server: {message}\n")
    s.sendall(message.encode('utf8'))

def ready_up_test():
    HOST = "127.0.0.1"
    PORT = 7070
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.connect((HOST, PORT))
        BUFFER_SIZE = 1024
        my_id = 0
        host_id = 0

        my_socket.send("Req_Data-String-my_id".encode("utf8"))
        my_id = my_socket.recv(BUFFER_SIZE).decode("utf8")

        print(f"You are player: {my_id}")


        index = 0
        while True:
            time.sleep(3)
            my_socket.send("Req_Data-String-lobby_state".encode("utf8"))
   
            data = my_socket.recv(BUFFER_SIZE).decode("utf8")
            print(f"Recived: {data}")

            tokens = data.split('-')

            if(tokens[0] == "READY_UPStart_Game" or tokens[0] == "Start_Game"):
                break

            if(tokens[0] == "Host_Number"):

                host_id = tokens[1]
     
            #on 5th loop client can choose to ready up (only here for testing change as needed)
            if(index == 2):
                userTestInput = input("Who would you like to vote for? (#): ")

                my_socket.send(f"Vote_Host-{userTestInput}".encode("utf8"))
               
         
            if(index == 4):
                userTestInput = input("Would you like to ready up? ('y' or 'n'): ")


                if(userTestInput == "y"):
                    my_socket.send("Ready_Up-1".encode("utf8"))

            index += 1

        while True:

           
            time.sleep(3)
        
            my_socket.send("Req_Data-String-game_state".encode("utf8"))
           
            BUFFER_SIZE = 1024
   
            data = my_socket.recv(BUFFER_SIZE).decode("utf8")
            print(f"Received From Game Loop: {data}")

        

            if(data == "SENDING_QUESTION"):
                 my_socket.send("Received_Question-NA".encode("utf8"))

            
            if(data == "WAITING_FOR_BUZZ"):

                if(host_id != my_id):

                    userTestInput = input("Would you like to buzz in? ('y' or 'n'): ")
                    if(userTestInput == "y"):
                        my_socket.send("Buzzing-NA".encode("utf8"))

            
            if(data == "WAITING_FOR_HOSTS_CHOICE"):

                if(host_id == my_id):
                    userTestInput = input("You are the host: is the answer correct or not? ('y' or 'n'): ")
                    if(userTestInput == "y"):
                        my_socket.send("Host_Choice-Y".encode("utf8"))
                    else:
                        my_socket.send("Host_Choice-N".encode("utf8"))

if __name__ == '__main__':
    ready_up_test()