#!/usr/bin/python3

import requests
import subprocess
from msal import PublicClientApplication

# Needs to come out of configuration
MSAL_CLIENT_ID = ""

SCOPES_NEEDED = ["XboxLive.signin"]

# Many of these constants are part of how the responses from various
# authentication endpoints are expected to be strutured.
# Usually if an expected key is missing, an error will be thrown and
# the program will move on to attempting the next account's authentication.
AUTHORITY_URL = "https://login.microsoftonline.com/consumers"

MSAL_TOKEN_KEY = "access_token"
MSAL_ERROR_KEYS = ("error", "error_description", "correlation_id")

XBL_URL = "https://user.auth.xboxlive.com/user/authenticate"
XBL_TOKEN_KEY = "Token"

# This structure defines how to find the xboxlive hash
# in the json returned from xboxlive authentication.
# Each tuple is either (key, dict) or (index, list)
# This tells you that the json object you're currently
# looking at is expected to be either
# 1) a dictionary and you should extract whatever is under the specified key
# or 2) a list and you should extract whatever is at the specified index
# Keep doing this recursively until you reach the end of the 'PARTS' tuple
# and you should have the hash.
XBL_HASH_STEPS = (("DisplayClaims", dict), ("xui", dict), (0, list), ("uhs", dict))


def get_xboxlive_hash(xbljson):

    json_object = xbljson

    for stage in XBL_HASH_STEPS:
        assert len(stage) == 2, "Variable defining location of XboxLive hash was incorectly structured: {}".format(XBL_HASH_STEPS)
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
            raise AssertionError("Variable defining location of XboxLive hash must have each stage be either a list or dictionary. Was {}".format(XBL_HASH_STEPS))


def msal_result_error(result):
    for key in MSAL_ERROR_KEYS:
        if key in result:
            print(result[key])


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
    auth_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    xboxlive_resp = requests.post(XBL_URL, json=xboxlive_props, headers=auth_headers)
    xbljson = xboxlive_resp.json()

    if XBL_TOKEN_KEY in xbljson:
        xbltok = xbljson[XBL_TOKEN_KEY]
    else:
        raise ValueError("Expected XboxLive authentication response to contain {}. Instead it was {}".format(XBL_TOKEN_KEY, xbltok))

    xblhash = get_xboxlive_hash(xbljson)


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
        auth_xboxlive(result)

def auth_all(ms_usernames):
    assert isinstance(ms_usernames, list), "Must pass a list of usernames to auth_all. Was given {}".format(type(ms_usernames))
    for accname in ms_usernames:
        assert isinstance(accname, str), "List passed to auth_all must be made of strings. Found a {}".format(type(accname))

    app = PublicClientApplication(
        MSAL_CLIENT_ID,
        authority = AUTHORITY_URL
    )

    for accname in ms_usernames:
        auth_account(accname)
