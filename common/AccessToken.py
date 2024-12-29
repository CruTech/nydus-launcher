
import datetime
from nydus.common import validity

class AccessToken:

    """
    token: nonempty string representing some access token
    expire_time: a datetime object, the point at which the token expires
    tokhash: a hash that goes with the token; needed for some Xbox tokens
    """
    def __init__(self, token, expire_time, tokhash=""):

        if not validity.is_nonempty_str(token):
            raise ValueError("token value given to AccessToken class must be a nonempty string. Instead, was given {}".format(token))

        if not isinstance(expire_time, datetime.datetime):
            raise ValueError("Expiry time given to AccessToken class must be in the form of a datetime object. Instead, was given {}".format(expire_time))

        self.token = token
        self.expire_time = expire_time
        self.tokhash = tokhash

    def get_token(self):
        return self.token

    def get_expiry(self):
        return self.expire_time

    def get_hash(self):
        return self.tokhash

    def is_expired(self):
        return self.expire_time < datetime.datetime.now()
