import random


#### Application logic for game
# use list of Players, not Client
MIN_PLAYERS = 3


#### Get current state of game
def get_game_state(players, last_state):
    nplayers = len(players)
  
 
    if (last_state == "SENDING_QUESTION"):

        total_views = did_all_players_view_question(players)

        if(total_views < nplayers):
            return "SENDING_QUESTION"
        else:
            return "WAITING_FOR_BUZZ"
      
   
    elif last_state == "WAITING_FOR_BUZZ":

        if(did_somone_buzz):
            return "SOMEONE_BUZZED"
        else:
            return "WAITING_FOR_BUZZ"
    
    elif last_state == "SOMEONE_BUZZED":

        return "WAITING_FOR_ANSWER"
   
    elif last_state == "WAITING_FOR_ANSWER":
       
        return "GOT_ANSWER"
   
    elif last_state == "GOT_ANSWER":
        pass

    elif last_state == "WAITING_FOR_HOST_CHOICE":
        pass
    
    elif last_state == "GOT_HOST_CHOICE":
        pass

    elif last_state == "GAME_OVER":
        return "ENDING_GAME"

    elif last_state == "ENDING_GAME":
        pass
 

        
    return "INVALID_STATE"


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
       
       
