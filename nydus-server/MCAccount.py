
class MCAccount:

    def __init__(self, username, uuid, token):
        assert isinstance(username, str), "Minecraft username should have been string; was {}".format(username)
        assert isinstance(uuid, str), "Minecraft uuid should have been string; was {}".format(uuid)
        assert isinstance(token, str), "Minecraft token should have been string; was {}".format(token)
        self.username = username
        self.uuid = uuid
        self.token = token

    def get_username(self):
        return self.username

    def get_uuid(self):
        return self.uuid

    def get_token(self):
        return self.token
