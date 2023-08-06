import socket
import time
import pickle
from threading import Thread
from queue import Queue
""""import streamlit as st
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
        if streamlit_loop:
            streamlit_loop.call_soon_threadsafe(notify)

# Close and delete socket when Server disconnects
def server_disconnect():
    st.session_state['server_disconnect'] = True
    st.session_state.my_socket.close()
    del st.session_state.my_socket
    time.sleep(.1)
    if streamlit_loop:
        streamlit_loop.call_soon_threadsafe(notify)

def req_data_from_server(s, request):
    message = f"Req_Data-String-{request}\n" 
    print(f"...sending message to server: {message}")
    s.send(message.encode('utf8'))

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

#### Data Strings need to be decoded with utf8
def req_data_string(s, string):
    message = f"Req_Data-String-{string}\n" 
    print(f"...sending message to server: {message}")
    s.send(message.encode('utf8'))"""


def threaded_function(message_queue, my_socket):

    BUFFER_SIZE = 1024
    while(True):

        try: 
            recv = my_socket.recv(BUFFER_SIZE)
            message = recv.decode("utf-8")

        except UnicodeDecodeError: # If decoding doesn't work, message is not a string. Deserialize with pickle
            message = pickle.loads(recv)
            to_console = "{ header: " + message['header'] + ", label: " + message['label'] + ", data: " + str(message['data'])[:50] + "... }"
            #print(f"Received message from server: {to_console}\n")
            message_queue.put(message)
        



def ready_up_test():
    HOST = "127.0.0.1"
    PORT = 7070

    message_queue = Queue()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((HOST, PORT))
 
        
    
    #------------------------------------------------------
    thread = Thread(target = threaded_function, args = (message_queue, my_socket))
    thread.start()
    #----------------------------------------------------

    
    my_id = 0
    host_id = 0


    index = 0
    my_socket.send("Req_Data-String-my_id".encode("utf8"))

    voted = False
    readied_up = False
    
    while True:
      
      
        isString = False
        
        message = message_queue.get()

      

        my_socket.send("Req_Data-String-lobby_state".encode("utf8"))
    

        
            
        if(str(message['data'])[:10] == "READY_UPStart_Game" or str(message['data'])[:10] == "START_GAME"):
            break
        elif((str(message['label'])[:10] == "my_id")):

            my_id = str(message['data'])[:10]

            print("My id is: ")
            print(str(message['data'])[:10])
            print("\n")
        
        elif(str(message['label'])[:10] == "host_id"):
                
                host_id = str(message['data'])[:10]
                print("host: ")
                print(host_id)
                print("\n")
        
        #on 5th loop client can choose to ready up (only here for testing change as needed)

        if(voted == False):
  
            if(str(message['data'])[:10] == "VOTE"):
       
                userTestInput = input("Who would you like to vote for? (#): ")

                my_socket.send(f"Vote_Host-{userTestInput}".encode("utf8"))
                voted = True


        if(readied_up == False):

            if(str(message['data'])[:10] == "READY_UP"):
                userTestInput = input("Would you like to ready up? ('y' or 'n'): ")


                if(userTestInput == "y"):
                    my_socket.send("Ready_Up-1".encode("utf8"))
                    readied_up = True
    

        index += 1

    print("left lobby loop\n")
    while True:

        message = message_queue.get()
        print(str(message['data'])[:20])
        my_socket.send("Req_Data-String-game_state".encode("utf8"))

        if(str(message['data'])[:20] == "SENDING_QUESTION"):
                print("sending recieved question\n")
                my_socket.send("Received_Question-NA".encode("utf8"))


        if(str(message['data'])[:20] == "WAITING_FOR_BUZZ"):

            if(host_id != my_id):

                userTestInput = input("Would you like to buzz in? ('y' or 'n'): ")
                if(userTestInput == "y"):
                    my_socket.send("Buzzing-NA".encode("utf8"))


        if(str(message['data'])[:20] == "WAITING_FOR_HOSTS_CHOICE"):

            if(host_id == my_id):
                userTestInput = input("You are the host: is the answer correct or not? ('y' or 'n'): ")
                if(userTestInput == "y"):
                    my_socket.send("Host_Choice-Y".encode("utf8"))
                else:
                    my_socket.send("Host_Choice-N".encode("utf8")) 

if __name__ == '__main__':
    ready_up_test()