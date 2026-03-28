import json
import os
import time
from pathlib import Path
import requests

TRAKT_API_URL = "https://api.trakt.tv"
DEVICE_CODE_URL = f"{TRAKT_API_URL}/oauth/device/code"
DEVICE_TOKEN_URL = f"{TRAKT_API_URL}/oauth/device/token"
TOKEN_STATE_PATH = Path("token_state.json")

CLIENT_ID = os.environ["TRAKT_CLIENT_ID"]
CLIENT_SECRET = os.environ["TRAKT_CLIENT_SECRET"]


def load_token_state():
    if not TOKEN_STATE_PATH.exists():
        return None
    with TOKEN_STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_token_state(data):
    with TOKEN_STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def refresh_token(state):
    refresh_token = state.get("refresh_token")
    if not refresh_token:
        return None

    resp = requests.post(
        f"{TRAKT_API_URL}/oauth/token",
        json={
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "refresh_token",
        },
        headers={"Content-Type": "application/json"},
    )

    if resp.status_code != 200:
        print(f"[token_manager] Refresh failed: {resp.status_code} {resp.text}")
        return None

    data = resp.json()
    save_token_state(data)
    print("[token_manager] Token refreshed successfully")
    return data


def start_device_flow():
    resp = requests.post(
        DEVICE_CODE_URL,
        json={"client_id": CLIENT_ID},
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    data = resp.json()

    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_url = data["verification_url"]
    interval = data.get("interval", 5)
    expires_in = data.get("expires_in", 600)

    print("[token_manager] Trakt device authorization required.")
    print(f"[token_manager] Go to: {verification_url}")
    print(f"[token_manager] Enter code: {user_code}")
    print("[token_manager] This is a one-time action.")

    start = time.time()
    while True:
        if time.time() - start > expires_in:
            raise RuntimeError("Device code expired before authorization.")

        resp = requests.post(
            DEVICE_TOKEN_URL,
            json={
                "code": device_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/json"},
        )

        if resp.status_code == 200:
            token_data = resp.json()
            save_token_state(token_data)
            print("[token_manager] Device authorized and token obtained.")
            return token_data

        time.sleep(interval)


def ensure_token():
    state = load_token_state()

    if state:
        refreshed = refresh_token(state)
        if refreshed:
            return refreshed
        print("[token_manager] Refresh failed, falling back to device flow.")

    return start_device_flow()


if __name__ == "__main__":
    ensure_token()
    print("[token_manager] Access token ready.")
