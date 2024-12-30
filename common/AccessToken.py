
import datetime
from nydus.common import validity

# This class is used to store access tokens along with their expiries
# Some tokens also come with hashes we need to store; mainly the Xbox ones.

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

    """
    check_inteval: a timedelta representing how long it will be until
    the next time the token expiry is checked
    Returns True if the token needs renewal, False otherwise.
    Token needs renewal if it is currently expired or will be
    before it is checked again.
    """
    def needs_renewal(self, check_interval):
        if not isintance(check_interval, datetime.timedelta):
            raise TypeError("check_interval for AccessToken.needs_renewal must be a datetime.timedelta. Was given a {}".format(type(check_interval)))

        if self.is_expired():
            return True

        if datetime.datetime.now() + check_interval > self.get_expiry():
            return True

        return False
