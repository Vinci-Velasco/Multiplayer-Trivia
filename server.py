import socket
import threading
import time
from queue import Queue

HOST = "127.0.0.1"
PORT = 7070



# Thread that deals with listening to clients
def listening_thread(client_socket, addr, message_queue):
    BUFFER_SIZE = 1024 # change size when needed
    with client_socket:
        while True:
            message = client_socket.recv(BUFFER_SIZE).decode("utf8")
            print(f"Recieved message from {addr}")
            message_queue.put((message, addr))
            client_socket.send("Server acknowledges your message\n".encode())
          

# Custom thread class that creates new threads once connections come in
class Recieve_Connection_Thread(threading.Thread):
    def __init__(self, server, message_queue):
        super().__init__()
        self.server = server
        self.message_queue = message_queue
        self.stop_connections = False

    # Listens to connections and creates new threads. Closes once max connections achieved
    # or stop_connections is set to True (via the stop() method)
    def run(self):
        connections = 0
        MAX_CONNECTIONS = 5

        while connections < MAX_CONNECTIONS:
            print(f"Listening for connections ({connections}/{MAX_CONNECTIONS})...")
            client_socket, addr = self.server.accept()

            # terminate thread if stop_connections set to True
            if self.stop_connections:
                break

            # otherwise create new thread for connection
            client_sockets.append(client_socket)
            client_addrs.append(addr)
            thread = threading.Thread(
                target=listening_thread, args=(client_socket, addr, self.message_queue))
            thread.start()
            connections += 1
            playerNumber[addr] = connections, client_socket
            client_socket.send(f"Connection to server established. You're Player #{connections}\n".encode("utf8"))

           
            for client_socket in client_sockets:
               
                client_socket.send(str(f"Players: {client_addrs} are in the lobby!\n").encode("utf8"))

        print(f"Done with connections ({connections}/{MAX_CONNECTIONS})")

    # Stop the thread by changing the stop_connections cond to True and unblocking the
    # server.accept() call. This is safer than killing the thread as it can terminate properly
    def stop(self):
        self.stop_connections = True
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((HOST, PORT))

def allPlayersReady(ready_clients):
    index = 0
    proceedOrNot = True


    for allClients in client_sockets:
            
        if(ready_clients[index] == False):

            for client in client_sockets:
                # send data to all clients
               
                #commented out until a solution for slowing down the rate of sending is found
                #client.send(str(f"Waiting on Player {index + 1} to ready up!\n").encode("utf8"))
                proceedOrNot = False
                
        index += 1
    return proceedOrNot


#Token functions-------------------------------------------------------------------------------------

def readyUp(ready_clients, playerNumber, client_sockets):

    ready_clients[playerNumber-1] = True
    client_sockets[playerNumber-1].send("Server Acknowlegdes Ready Up\n".encode("utf8"))

    return ready_clients

def hostChoice():
    pass

def voteHost():
    pass

def answer():
    pass

def buzzing():
    pass

#Token functions-------------------------------------------------------------------------------------


if __name__ == "__main__":
    # setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM = TCP
    server.bind((HOST, PORT))
    server.listen()

    # data structures to hold client sockets and message queue so main can communicate
    # with listening threads and vice versa
    client_sockets = []
    client_addrs = []

    playerNumber = {}

    ready_clients = [False, False, False, False, False]
    message_queue = Queue() # locks are already built in to Queue class
    recieve_connections_thread = Recieve_Connection_Thread(server, message_queue)
    recieve_connections_thread.start()

    # lobby loop
    host_voted = False
    all_ready = False
    while not (all_ready and host_voted):


        message, addr = message_queue.get()
    
        print(message)

        # application layer protocol for lobby (parse tokens)
    
    #Token Parse------------------------------------------------------------------
        splitMessage = message.split('-')

        if (splitMessage[0] == "Vote_Host"):
               pass

        elif (splitMessage[0] == "Vote_Host"):
            pass

        elif (splitMessage[0] == "Ready_Up"):

            ready_Clients = readyUp(ready_clients, playerNumber[addr][0], client_sockets)
            

        
        
    #Token Parse------------------------------------------------------------------

        all_ready = allPlayersReady(ready_clients)
        # If all players are ready move on to the main game loop
        if all_ready == True:
  
            break

         
                

    # close ability to connect
    recieve_connections_thread.stop()
    recieve_connections_thread.join()

    # send info to clients that main game has started
    # ...

    # main game loop
    game_loop = True
    while game_loop:
        message, addr = message_queue.get()
        print(message)

         # application layer protocol for game loop (parse tokens)
         # ...

        splitMessage = message.split('-')

       #Token Parse------------------------------------------------------------------

        if (splitMessage[0] == "Buzzing"):
               pass

        elif (splitMessage[0] == "Host_Choice"):
            pass

        #Token Parse------------------------------------------------------------------
         


