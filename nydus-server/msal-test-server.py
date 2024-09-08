#!/usr/bin/python3

import requests
from msal import PublicClientApplication

SCOPES_NEEDED = ["XboxLive.signin"]


#
# Authenticate to Microsoft
#

app = PublicClientApplication(
        "Your client ID here",
        authority="https://login.microsoftonline.com/consumers")

result = None

accounts = app.get_accounts()

if accounts:

    chosen = accounts[0]

    result = app.acquire_token_silent(SCOPES_NEEDED, account=chosen)

if not result:
    result = app.acquire_token_interactive(scopes=SCOPES_NEEDED)

if "access_token" in result:
    print(result["access_token"])

else:
    print(result["error"])
    print(result["error_description"])
    print(result["correlation_id"])
    exit()


#
# Authenticate to XboxLive
#

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

xboxlive_resp = requests.post("https://user.auth.xboxlive.com/user/authenticate",
        json=xboxlive_props, headers=auth_headers)
xbljson = xboxlive_resp.json()

xbltok = xbljson["Token"]
xblhash = xbljson["DisplayClaims"]["xui"][0]["uhs"]

#
# Get Xbox Services Security Token
#

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

xsts_resp = requests.post("https://xsts.auth.xboxlive.com/xsts/authorize",
        json=xsts_props, headers=auth_headers)

xstsjson = xsts_resp.json()
xststok = xstsjson["Token"]
xstshash = xstsjson["DisplayClaims"]["xui"][0]["uhs"]
assert xstshash == xblhash

#
# Authenticate to Minecraft
#

minecraft_props = {
    "identityToken": "XBL3.0 x={};{}".format(xstshash, xststok)
}

minecraft_resp = requests.post("https://api.minecraftservices.com/authentication/login_with_xbox",
        json=minecraft_props, headers=auth_headers)

mc_json = minecraft_resp.json()
mc_access_tok = mc_json["access_token"]

#
# Get profile uuid
#

auth_headers["Authorization"] = "Bearer {}".format(mc_access_tok)

profile_resp = requests.get("https://api.minecraftservices.com/minecraft/profile",
        headers=auth_headers)

profile_json = profile_resp.json()

mc_username = profile_json["name"]
mc_uuid = profile_json["id"]

# Pass mc_username, mc_uuid, mc_access_tok to client
