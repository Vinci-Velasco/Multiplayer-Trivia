class Player:
    def __init__(self, id):
        self.id = id

        # initial instance values
        self.votes = 0
        self.score = 0
        self.is_host = False
        self.already_voted = False