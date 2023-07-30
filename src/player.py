class Player:
    def __init__(self, id, is_me=False):
        self.id = id
        self.is_me = is_me 

        # initial instance values
        self.votes = 0
        self.score = 0
        self.is_host = False
        self.voted = False