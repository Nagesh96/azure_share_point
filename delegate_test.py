# graph_handshake_test.py
# Purpose: Quick "handshake" test using Delegated auth (Device Code).
# Verifies token acquisition and makes a few simple Microsoft Graph calls.

import os
import sys
import json
import requests
from azure.identity import DeviceCodeCredential

# ---- REQUIRED: fill these two values ----
TENANT_ID = "<YOUR_TENANT_ID>"   # e.g., 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
CLIENT_ID = "<YOUR_CLIENT_ID>"   # the App (client) ID you received
# ----------------------------------------

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH = "https://graph.microsoft.com/v1.0"

def get_token():
    # DeviceCodeCredential will print a code and URL to complete sign-in
    cred = DeviceCodeCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID)
    token = cred.get_token(GRAPH_SCOPE).token
    return token

def call_graph(token, url):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, timeout=30)
    return r

def pretty(obj):
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)

def main():
    missing = []
    if not TENANT_ID or TENANT_ID.startswith("<"):
        missing.append("TENANT_ID")
    if not CLIENT_ID or CLIENT_ID.startswith("<"):
        missing.append("CLIENT_ID")
    if missing:
        print(f"Please set: {', '.join(missing)}")
        sys.exit(1)

    print("Acquiring token via Device Code (Delegated)...")
    try:
        token = get_token()
        print("✔ Token acquired.")
    except Exception as e:
        print("✖ Failed to acquire token.")
        print(e)
        sys.exit(1)

    # 1) Simple sanity check: who am I?
    print("\nCalling /me ...")
    r = call_graph(token, f"{GRAPH}/me")
    print(f"Status: {r.status_code}")
    try:
        print(pretty(r.json()))
    except Exception:
        print(r.text)

    # 2) Optional: list your SharePoint followed sites (works with user perms)
    print("\nCalling /me/followedSites ... (may be empty if you don't follow sites)")
    r = call_graph(token, f"{GRAPH}/me/followedSites")
    print(f"Status: {r.status_code}")
    try:
        print(pretty(r.json()))
    except Exception:
        print(r.text)

    # 3) Optional: list your OneDrive root children (proves basic SharePoint/Files reach)
    print("\nCalling /me/drive/root/children ... (requires OneDrive access)")
    r = call_graph(token, f"{GRAPH}/me/drive/root/children")
    print(f"Status: {r.status_code}")
    try:
        print(pretty(r.json()))
    except Exception:
        print(r.text)

    print("\nDone. If /me returned 200 and user details, your App Registration works with Delegated auth.")

if __name__ == "__main__":
    main()
