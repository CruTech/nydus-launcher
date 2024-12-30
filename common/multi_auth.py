#!/usr/bin/python3

import requests
import subprocess
from msal import PublicClientApplication
from nydus.common.MCAccount import MCAccount

MS_USERNAMES = []

# Needs to come out of configuration
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
            print("Variable defining location of Xbox hash was incorectly structured: {}".format(XBL_HASH_STEPS))
            return None
        wanted_type = stage[1]

        if not isinstance(json_object, wanted_type):
            print("Expect json object to be {} but was {}".format(wanted_type, type(json_object)))
            return None

        if wanted_type == dict:
            wanted_key = stage[0]

            if not wanted_key in json_object:
                print("Json object did not have expected key {}. It was {}".format(wanted_key, json_object))
                return None
            
            json_object = json_object[wanted_key]

        elif wanted_type == list:
            wanted_idx = stage[0]

            if len(json_object) - 1 < wanted_idx:
                print("Json object did not have expected index {}. It was {}".format(wanted_idx, json_object))
                return None

            json_object = json_object[wanted_idx]

        else:
            print("Variable defining location of Xbox hash must have each stage be either a list or dictionary. Was {}".format(XBL_HASH_STEPS))
            return None

    if not isinstance(json_object, str):
        raise ValueError("No string found at expected location of Xbox hash. Instead got {}".format(json_object))

    return json_object


def msal_result_error(result):
    for key in MSAL_ERROR_KEYS:
        if key in result:
            print(result[key])

"""
Given a dictionary as returned by MSAL authentication
(it must contain the access_token key) this function
authenticates to xbox live and returns a tuple
(token, hash)
A tuple is always returned or an exception is raised.
If the token or hash cannot be found, None will be
substituted in that place in the tuple.
"""
def auth_xboxlive(result):
    assert isinstance(result, dict), "Must pass a dictionary, the result of MSAL authentication, to auth_xboxlive. Got {}".format(result)
    assert MSAL_TOKEN_KEY in result, "MSAL Auth result dictionary given to auth_xboxlive must contain {}. Instead, the given dictionary was: {}".format(MSAL_TOKEN_KEY, result)

    xboxlive_props = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d={}".format(result["access_token"])
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }

    xboxlive_resp = requests.post(XBL_URL, json=xboxlive_props, headers=AUTH_HEADERS)
    xbljson = xboxlive_resp.json()

    xbltok = None
    if XB_TOKEN_KEY in xbljson:
        xbltok = xbljson[XB_TOKEN_KEY]
    else:
        print("Expected XboxLive authentication response to contain {}. Instead we could not get the token, and the response was {}".format(XBL_TOKEN_KEY, xbltok))

    xblhash = get_xbox_hash(xbljson)
    if xblhash == None:
        print("Failed to get XboxLive hash for an account.")

    return xbltok, xblhash

def auth_xsts(xbltok):
    assert isinstance(xbltok, str), "XboxLive token given to auth_xsts must be a string. Got {}".format(xbltok)

    xsts_props = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                xbltok
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }

    xsts_resp = requests.post(XSTS_URL, json=xsts_props, headers=AUTH_HEADERS)

    xstsjson = xsts_resp.json()

    xststok = None
    if XB_TOKEN_KEY in xstsjson:
        xststok = xstsjson[XB_TOKEN_KEY]
    else:
        print("Expected XSTS response to contain {}. Instead we could not get the token, and response was {}".format(XB_TOKEN_KEY, xstsjson))

    xstshash = get_xbox_hash(xstsjson)
    if xstshash == None:
        print("Failed to get XSTS hash for an account.")

    return xststok, xstshash

"""
Takes in the XSTS token and XSTS hash (in that order),
authenticates to Minecraft, and if successful returns
the access token for Minecraft.
"""
def auth_minecraft(xststok, xstshash):
    minecraft_props = {
        "identityToken": "XBL3.0 x={};{}".format(xstshash, xststok)
    }

    minecraft_resp = requests.post(MC_AUTH_URL,
            json=minecraft_props, headers=AUTH_HEADERS)

    mc_json = minecraft_resp.json()
    
    mc_access_tok = None
    if MC_TOKEN_KEY in mc_json:
        mc_access_tok = mc_json[MC_TOKEN_KEY]
    else:
        print("Key {} was missing from Minecraft authentication response. Response was {}".format(MC_TOKEN_KEY, mc_json))

    return mc_access_tok

"""
Given the Minecraft access token received from authenticating,
this function returns a tuple
(username, uuid)
Which are the username and uuid of the authenticated
account. These are needed for manual Minecraft launch.
A tuple is always returned. None will be substituted in
the relevant location if a piece of data cannot be found.
"""
def get_minecraft_details(mc_access_tok):
    profile_headers = AUTH_HEADERS.copy()
    profile_headers["Authorization"] = "Bearer {}".format(mc_access_tok)

    profile_resp = requests.get(MC_PROFILE_URL, headers=profile_headers)

    profile_json = profile_resp.json()

    mc_username = profile_json.get(MC_USERNAME_KEY)

    mc_uuid = profile_json.get(MC_UUID_KEY)

    if mc_username == None:
        print("Key {} was missing from Minecraft profile response. Response was {}".format(MC_USERNAME_KEY, profile_json))

    if mc_uuid == None:
        print("Key {} was missing from Minecraft profile response. Response was {}".format(MC_UUID_KEY, profile_json))

    return (mc_username, mc_uuid)
"""
Given a dictionary as returned by MSAL authentication
(it must contain the access_token key) this function
performs the remaining authentication to reach a ready
to play Minecraft state and returns an MCAccount
containing the username, uuid, and token gotten.
"""
def auth_stream(result):
    assert isinstance(result, dict), "Must pass a dictionary, the result of MSAL authentication, to auth_stream. Got {}".format(result)
    assert MSAL_TOKEN_KEY in result, "MSAL Auth result dictionary given to auth_stream must contain {}. Instead, the given dictionary was: {}".format(MSAL_TOKEN_KEY, result)
    
    xbltok, xblhash = auth_xboxlive(result)

    if xbltok == None or xblhash == None:
        return None
    
    xststok, xstshash = auth_xsts(xbltok)

    if xststok == None or xstshash == None:
        return None

    assert xblhash == xstshash, "Hashes from XboxLive and Xbox Security Services differed. They were {} and {}".format(xblhash, xstshash)

    mc_access_tok = auth_minecraft(xststok, xstshash)

    mc_username, mc_uuid = get_minecraft_details(mc_access_tok)

    if not mc_access_tok:
        print("Could not get Minecraft access token for account")
        return None

    if not mc_username:
        print("Could not get Minecraft username for account")
        return None

    if not mc_uuid:
        print("Could not get Minecraft UUID for account")
        return None

    return MCAccount(mc_username, mc_uuid, mc_access_tok)

def auth_account(accname, app):
    assert isinstance(accname, str), "Must pass a string containing Microsoft account username (email address) to auth_account. Was given {} of {}".format(accname, type(accname))
    assert isinstance(app, PublicClientApplication), "Must pass an MSAL PublicClientApplication to auth_account. Got a  {}".format(type(app))

    accounts = app.get_accounts()

    result = None

    if accounts:

        # Using .get so we'll receive None if the key is absent
        found = [acc for acc in accounts if acc.get("username") == accname]

        if found:
            result = app.acquire_token_silent(SCOPES_NEEDED, account=found[0])

    if not result:
        result = app.acquire_token_interactive(scopes=SCOPES_NEEDED, login_hint=accname)

    if not MSAL_TOKEN_KEY in result:
        print("Error with MSAL trying to authenticate account {}".format(accname))
        print("Details follow:")
        msal_result_error(result)
        print()
    else:
        return auth_stream(result)

def auth_all(ms_usernames):
    assert isinstance(ms_usernames, list), "Must pass a list of usernames to auth_all. Was given {}".format(type(ms_usernames))
    for accname in ms_usernames:
        assert isinstance(accname, str), "List passed to auth_all must be made of strings. Found a {}".format(type(accname))

    app = PublicClientApplication(
        MSAL_CLIENT_ID,
        authority = AUTHORITY_URL
    )

    authd_accounts = []
    for accname in ms_usernames:
        acc_res = auth_account(accname, app)
        if acc_res:
            authd_accounts.append(acc_res)
        else:
            print("Failed to auth {}".format(accname))

    print("In total, authd {} accounts".format(len(authd_accounts)))
    for acc in authd_accounts:
        print(acc.get_username())

