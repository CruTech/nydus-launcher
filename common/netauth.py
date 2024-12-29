
import requests
from msal import PublicClientApplication
from nydus.common.MCAccount import MCAccount

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

