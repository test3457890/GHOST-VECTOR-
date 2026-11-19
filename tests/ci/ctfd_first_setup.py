"""CI helper: run first-time setup on a blank CTFd and save an admin API token.

Usage: python3 ctfd_first_setup.py http://localhost:8000 token.txt
Test use only. Never point this at a real event CTFd.
"""
import re
import sys

import requests

B = sys.argv[1].rstrip("/")
s = requests.Session()
html = s.get(B + "/setup").text
nonce = re.search(r'csrfNonce.\s*[:=]\s*"([0-9a-f]+)"', html).group(1)
data = {"ctf_name": "GHOST VECTOR Test", "ctf_description": "test", "user_mode": "users",
        "challenge_visibility": "private", "account_visibility": "public", "score_visibility": "public",
        "registration_visibility": "public", "verify_emails": "false", "team_size": "",
        "name": "admin", "email": "admin@example.com", "password": "AdminPass123!",
        "ctf_logo": "", "ctf_banner": "", "ctf_small_icon": "", "ctf_theme": "core",
        "theme_color": "", "start": "", "end": "", "social_shares": "true", "nonce": nonce, "_submit": "Finish"}
r = s.post(B + "/setup", data=data, allow_redirects=False)
print("setup", r.status_code)
assert r.status_code == 302, "setup failed"
html = s.get(B + "/challenges").text
nonce = re.search(r'csrfNonce.\s*[:=]\s*"([0-9a-f]+)"', html).group(1)
r = s.post(B + "/api/v1/tokens", json={"description": "ctfcli"}, headers={"CSRF-Token": nonce})
print("token", r.status_code)
print(r.json()["data"]["value"], file=open(sys.argv[2], "w"))
