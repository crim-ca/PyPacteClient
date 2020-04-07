import datetime


class Credential:

    def __init__(self, username, password, prenom=None, nom=None,
                 user_id=None, user_profile_id=None):

        self.username = username
        self.password = password
        self.prenom = prenom
        self.nom = nom
        self.userId = user_id
        self.userProfileId = user_profile_id
        self.token = None
        self.tokenCreation = None

    def setToken(self, new_token):

        if new_token and len(new_token) > 0:
            self.token = new_token
        else:
            self.token = None
        self.tokenCreation = datetime.datetime.now()
