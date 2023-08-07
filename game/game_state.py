#### Application logic for game
# use list of Players, not Client
MIN_PLAYERS = 3

class Game():
    def __init__(self, host, player_list=[]):
        self.player_list = player_list
        self.current_state = "SENDING_QUESTION"
        self.last_state = "START_GAME"
        self.current_question = None
        self.host = host
    
    def update_state(self, new_state):
        self.last_state = self.current_state
        self.current_state = new_state
        return new_state
    
    def update_players(self, player_list):
        self.player_list = player_list

    def state_changed(self):
        return not self.last_state == self.current_state

    def did_someone_buzz(self, player_list):
        for p in player_list:
            if p.has_lock == True:
                return True

        return False 
    
    #### Get current state of Lobby
    def get_state(self):
        state = self.current_state
        player_list = self.player_list
        num_players = len(player_list)

        if state == "END_GAME":
            return "END_GAME"
        
        ## Server will send out the question in this state to everyoe
        elif state == "SENDING_QUESTION":     
            total_views = did_all_players_view_question(player_list)

            if total_views < num_players:
                return self.update_state("SENDING_QUESTION")
            else:
                return self.update_state("WAITING_FOR_BUZZ")
            
        ## Game is waiting for any player to click the buzzer
        elif state == "WAITING_FOR_BUZZ":
            if self.did_someone_buzz(player_list) == True:
                return self.update_state("SOMEONE_BUZZED")
            else:
                return self.update_state("WAITING_FOR_BUZZ")
        
        ## A player has the buzzer. Wait for answer or buzzer timeout, handled on server-side
        elif state == "SOMEONE_BUZZED":
            return self.update_state("SOMEONE_BUZZED")

        ## Host is reviewing player's answer
        elif state == "WAITING_FOR_HOSTS_CHOICE":
            #SERVER NEEDS TO manually change state to GOT_HOST_CHOICE
            return self.update_state("WAITING_FOR_HOSTS_CHOICE")        
        
        ## Received Host's verification. Clients will wait until server finishes transitioning into the next level of the Game.
        elif state == "GOT_HOST_CHOICE":
            #server should give a player a point if they got the answer correct (not sure if we move on to a different question if client is wrong)
            return "GOT_HOST_CHOICE"
            #SERVER can manually decide to change state to sending question or back to waiting for buzz

        #server says game is over and which player won/display all points?
        elif state == "GAME_OVER":
            return "ENDING_GAME"

        #actually start shutting game down
        elif state == "ENDING_GAME":
            pass
    
        return "Game_INVALID_STATE_GAME"
        
    
def get_state(players, last_state):
    nplayers = len(players)
    
    #we can change these states if needed this is just how I thought the game woudl run -Parm
    
    #Server will send out the question in this state to everyoe
    if (last_state == "SENDING_QUESTION"):

        #make sure everyone got a chance to see the question before someone is allowed to buzz in 
        total_views = did_all_players_view_question(players)

        if(total_views < nplayers):
            return "SENDING_QUESTION"
        else:
            return "WAITING_FOR_BUZZ"
      
    #Server waits until a token is parsed which is a buzz
    elif last_state == "WAITING_FOR_BUZZ":


        if(did_somone_buzz(players) == True):
            return "SOMEONE_BUZZED"
        else:
            return "WAITING_FOR_BUZZ"
    
    #not really needed as a state but makes in easier to comprehend what is happening in the game
    elif last_state == "SOMEONE_BUZZED":

        return "WAITING_FOR_ANSWER"
   
    #server should start a timer thread during this statge 
    elif last_state == "WAITING_FOR_ANSWER":
       
        #SERVER NEEDS TO manually change state to got answer or waiting for buzz state (depending on if the tiemr went off or not)
        return "WAITING_FOR_ANSWER"
   
    #not really needed as a state but makes in easier to comprehend what is happening in the game
    elif last_state == "GOT_ANSWER":
        return "WAITING_FOR_HOSTS_CHOICE"

    #server should loop unil host has made a decision or until a timer expires (not sure we are timing the host)
    elif last_state == "WAITING_FOR_HOSTS_CHOICE":
        
        #SERVER NEEDS TO manually change state to GOT_HOST_CHOICE
        return "WAITING_FOR_HOSTS_CHOICE"
    
    #server should give a player a point if they got the answer correct (not sure if we move on to a different question if client is wrong)
    elif last_state == "GOT_HOST_CHOICE":

        
        return "GOT_HOST_CHOICE"

        #SERVER can manually decide to change state to sending question or back to waiting for buzz

    #server says game is over and which player won/display all points?
    elif last_state == "GAME_OVER":
        return "ENDING_GAME"

    #actually start shutting game down
    elif last_state == "ENDING_GAME":
        pass
 
    return "Game_INVALID_STATE_GAME"


def did_all_players_view_question(players):
    total_views = 0
    for p in players:
        if p.received_question:
            total_views +=1


    return total_views

def did_somone_buzz(players):
    for p in players:
        if p.has_lock == True:
            return True

    return False 

def has_someone_won(players):

    #If a player gets 3 questions right the game ends (can change number as needed)
    for p in players:
        if p.score >= 3:
            return True
        
    return False
       
       
