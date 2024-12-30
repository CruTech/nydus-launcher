
import requests
from msal import PublicClientApplication
from nydus.common.MCAccount import MCAccount
from nydus.common import validity
from nydus.common.AccessToken import AccessToken

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
# Xbox expiry given as a timestamp
XB_EXPIRY_KEY = "NotAfter"
XB_TOKEN_KEY = "Token"

XSTS_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"

MC_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
MC_TOKEN_KEY = "access_token"
# Minecraft expiry given as seconds from now
MC_EXPIRES_KEY = "expires_in"

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


"""
access_token: an AccessToken object obtained through MSAL. The caller
    needs to make sure it's valid and unexpired.
Returns an AccessToken object containing a token, expiry time, and a hash
for Xbox Live.
"""
def get_tok_xboxlive(access_token):
    if not isinstance(access_token, AccessToken):
        raise ValueError("An AccessToken class must be provided to get_tok_xboxlive. Instead, was given a {}".format(type(access_token)))

    if not validity.is_valid_msal_token(access_token.get_token()):
        raise ValueError("A valid MSAL token is needed to get an xboxlive token. Instead, was given {}".format(access_token))


    xboxlive_props = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d={}".format(access_token.get_token())
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }

    xboxlive_resp = requests.post(XBL_URL, json=xboxlive_props, headers=AUTH_HEADERS)
    xbljson = xboxlive_resp.json()

    if XB_TOKEN_KEY in xbljson:
        xbltok = xbljson[XB_TOKEN_KEY]
    else:
        raise KeyError("Expected XboxLive authentication response to contain {}. Instead we could not get the token, and the response was {}".format(XB_TOKEN_KEY, xbljson))

    xblhash = get_xbox_hash(xbljson)
    
    if XB_EXPIRY_KEY in xbljson:
        xblexpiry = parse_xbox_timestamp(xbljson[XB_EXPIRY_KEY])
    else:
        raise KeyError("Expected XboxLive authentication response to contain {}. Instead we could not get the timestamp, and the response was {}".format(XB_EXPIRY_KEY, xbljson))

    xbl_at = AccessToken(xbltok, xblexpiry, tokhash=xblhash)
    return xbl_at


"""
access_token: an AccessToken object obtained through auth to XboxLive. The caller
    needs to make sure it's valid and unexpired.
Returns an AccessToken object containing a token, expiry time, and a hash
for XSTS.
"""
def get_tok_xsts(access_token):
    if not isinstance(access_token, AccessToken):
        raise ValueError("An AccessToken class must be provided to get_tok_xsts. Instead, was given a {}".format(type(access_token)))

    if not validity.is_valid_xboxlive_token(access_token.get_token()):
        raise ValueError("A valid XboxLive token is needed to get an XSTS token. Instead, was given {}".format(access_token))


    xsts_props = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                access_token.get_token()
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }

    xsts_resp = requests.post(XSTS_URL, json=xsts_props, headers=AUTH_HEADERS)
    xstsjson = xsts_resp.json()

    if XB_TOKEN_KEY in xstsjson:
        xststok = xstsjson[XB_TOKEN_KEY]
    else:
        raise KeyError("Expected XSTS authentication response to contain {}. Instead we could not get the token, and the response was {}".format(XB_TOKEN_KEY, xstsjson))

    xstshash = get_xbox_hash(xstsjson)
    
    if XB_EXPIRY_KEY in xstsjson:
        xstsexpiry = parse_xbox_timestamp(xstsjson[XB_EXPIRY_KEY])
    else:
        raise KeyError("Expected XSTS authentication response to contain {}. Instead we could not get the timestamp, and the response was {}".format(XB_EXPIRY_KEY, xstsjson))

    xsts_at = AccessToken(xststok, xstsexpiry, tokhash=xstshash)
    return xsts_at


"""
access_token: an AccessToken object obtained through auth to XSTS. The caller
    needs to make sure it's valid and unexpired.
Returns an AccessToken object containing a token and expiry time for Minecraft.
"""
def get_tok_minecraft(access_token):
    if not isinstance(access_token, AccessToken):
        raise ValueError("An AccessToken class must be provided to get_tok_minecraft. Instead, was given a {}".format(type(access_token)))

    if not validity.is_valid_xsts_token(access_token.get_token()):
        raise ValueError("A valid XSTS token is needed to get a Minecraft token. Instead, was given {}".format(access_token))

    minecraft_props = {
        "identityToken": "XBL3.0 x={};{}".format(access_token.get_hash(), access_token.get_token())
    }

    minecraft_resp = requests.post(MC_AUTH_URL,
            json=minecraft_props, headers=AUTH_HEADERS)
    mc_json = minecraft_resp.json()

    if MC_TOKEN_KEY in mc_json:
        mc_access_tok = mc_json[MC_TOKEN_KEY]
    else:
        raise KeyError("Key {} was missing from Minecraft authentication response. Response was {}".format(MC_TOKEN_KEY, mc_json))

    if MC_EXPIRES_KEY in mc_json:
        mc_expiry_offset = mc_json[MC_EXPIRES_KEY]
    else:
        raise KeyError("Key {} was missing from Minecraft authentication response. Response was {}".format(MC_EXPIRES_KEY, mc_json))

    if validity.is_integer(mc_expiry_offset):
        expiry_dt = datetime.datetime.now() + datetime.timedelta(seconds = int(mc_expiry_offset))
    else:
        raise ValueError("Value of {} from Minecraft authentication response should be an integer representing seconds. Instead, was {}".format(MC_EXPIRES_KEY, mc_expiry_offset))

    mc_at = AccessToken(mc_access_tok, expiry_dt)
    return mc_at
