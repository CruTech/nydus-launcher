
import requests
from msal import PublicClientApplication
from nydus.common.MCAccount import MCAccount
from nydus.common import validity

# Utilities for authenticating to endpoints over the internet;
# Microsoft, Xbox, and Minecraft
# Used in getting and updating access tokens

MSAL_CLIENT_ID = ""

SCOPES_NEEDED = ["XboxLive.signin"]

# Many of these constants are part of how the responses from various
# authentication endpoints are expected to be strutured.
# Usually if an expected key is missing, an error will be thrown and
# the program will move on to attempting the next account's authentication.
AUTHORITY_URL = "https://login.microsoftonline.com/consumers"

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

MSAL_TOKEN_KEY = "access_token"
MSAL_ERROR_KEYS = ("error", "error_description", "correlation_id")

XBL_URL = "https://user.auth.xboxlive.com/user/authenticate"
XB_EXPIRY_KEY = "NotAfter"
XB_TOKEN_KEY = "Token"

XSTS_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"

MC_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
MC_TOKEN_KEY = "access_token"

MC_PROFILE_URL = "https://api.minecraftservices.com/minecraft/profile"
MC_USERNAME_KEY = "name"
MC_UUID_KEY = "id"

# This structure defines how to find the xboxlive hash
# in the json returned from xboxlive authentication.
# Each tuple is either (key, dict) or (index, list)
# This tells you that the json object you're currently
# looking at is expected to be either
# 1) a dictionary and you should extract whatever is under the specified key
# or 2) a list and you should extract whatever is at the specified index
# Keep doing this recursively until you reach the end of the 'PARTS' tuple
# and you should have the hash.
XB_HASH_STEPS = (("DisplayClaims", dict), ("xui", dict), (0, list), ("uhs", dict))

"""
Xbox timestamps are mostly easy to parse with datetime, but end in
decimal fractions of a second and the letter Z. The
decimal fractions of a second may be 6 or 7 digits long, so can't
easily be parsed with datetime.
This function handles that.
ts: nonempty string representing a timestamp as pulled from the json
in response to an xbox auth request.
It should be in the form
%Y-%m-%dT%H%:%M:%S.%QZ
(the -, T, :, ., and Z are literal)
all the %X entries in this format are as in the datetime module, with
the exception of %Q. In Xbox timestamps, that part of the time
is fractions of a second, but may have either 6 digits or 7.
To make it compatible with datetime, we simply ignore the 7th
digit if present.
Returns a datetime representing the same time.
"""
def parse_xbox_timestamp(ts):
    if not validity.is_valid_xbox_timestamp(ts):
        raise ValueError("Object given to parse_xbox_timestamp was not an Xbox timestamp. Should have been of the form {} but was given {}".format(XB_EXPIRY_FORMAT, ts))

    parts = ts.split(validity.XB_EXPIRY_SEPARATER)
    # We know there will be 2 parts because the timestamp validity check passed
    seconds_part = parts[0]
    fractional_part = parts[1]
    
    # Only keep 6 digits of the fractional part
    fractional_part = fractional_part.rstrip(validity.XB_EXPIRY_SUFFIX)
    fractional_part = "{:06d}".format(fractional_part)

    fixed_ts = "{}{}{}{}".format(seconds_part, validity.XB_EXPIRY_SEPARATER, fractional_part, validity.XB_EXPIRY_SUFFIX)
    xbox_datetime = datetime.datetime.strptime(fixed_ts, validity.XB_EXPIRY_FORMAT)
    return xbox_datetime

"""
Both XboxLive authentication and Xbox Security Services (XSTS)
have the same JSON structure with a hash in the same place
in the response to the posts we will be making.
This function extracts the hash from the json return structure
in both cases.
"""
def get_xbox_hash(xbjson):

    json_object = xbjson

    for stage in XB_HASH_STEPS:
        if len(stage) != 2:
            raise IndexError("Variable defining location of Xbox hash was incorectly structured: {}".format(XBL_HASH_STEPS))

        wanted_type = stage[1]

        if not isinstance(json_object, wanted_type):
            raise TypeError("Expect json object to be {} but was {}".format(wanted_type, type(json_object)))

        if wanted_type == dict:
            wanted_key = stage[0]

            if not wanted_key in json_object:
                raise KeyError("Json object did not have expected key {}. It was {}".format(wanted_key, json_object))
            
            json_object = json_object[wanted_key]

        elif wanted_type == list:
            wanted_idx = stage[0]

            if len(json_object) - 1 < wanted_idx:
                raise IndexError("Json object did not have expected index {}. It was {}".format(wanted_idx, json_object))

            json_object = json_object[wanted_idx]

        else:
            raise TypeError("Variable defining location of Xbox hash must have each stage be either a list or dictionary. Was {}".format(XBL_HASH_STEPS))

    if not isinstance(json_object, str):
        raise ValueError("No string found at expected location of Xbox hash. Instead got {}".format(json_object))

    return json_object


def get_tok_xboxlive(access_token):
    if not validity.is_valid_msal_token(access_token):
        raise ValueError("A valid MSAL token is needed to get an xboxlive token. Instead, was given {}".format(access_token))


    xboxlive_props = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d={}".format(access_token])
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }

    xboxlive_resp = requests.post(XBL_URL, json=xboxlive_props, headers=AUTH_HEADERS)
    xbljson = xboxlive_resp.json()

    if XB_TOKEN_KEY in xbljson:
        xbltok = xbljson[XB_TOKEN_KEY]
    else:
        raise KeyError("Expected XboxLive authentication response to contain {}. Instead we could not get the token, and the response was {}".format(XBL_TOKEN_KEY, xbltok))

    xblhash = get_xbox_hash(xbljson)

