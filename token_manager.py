import json
import time
import requests
import argparse
import os

TOKEN_FILE = "token_state.json"

CLIENT_ID = "c3f3f4f4c6f5c4e4b4e4a4d4c4b4a4d4"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # If needed for refresh flow

DEVICE_CODE_URL = "https://api.trakt.tv/oauth/device/code"
TOKEN_URL = "https://api.trakt.tv/oauth/token"


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def save_token(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def refresh_token_flow(token_data):
    print("🔄 Attempting refresh token...")

    payload = {
        "refresh_token": token_data["refresh_token"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "refresh_token"
    }

    try:
        r = requests.post(TOKEN_URL, json=payload)
        if r.status_code != 200:
            print(f"❌ Refresh failed: {r.status_code} {r.text}")
            return None

        new_data = r.json()
        new_data["created_at"] = int(time.time())
        save_token(new_data)

        print("✅ Refresh successful")
        return new_data

    except Exception as e:
        print(f"❌ Refresh error: {e}")
        return None


def device_flow():
    print("📱 Starting device flow...")

    payload = {"client_id": CLIENT_ID}
    r = requests.post(DEVICE_CODE_URL, json=payload)

    if r.status_code != 200:
        print(f"❌ Device code request failed: {r.status_code} {r.text}")
        return None

    data = r.json()
    print(f"➡️ Go to {data['verification_url']} and enter code: {data['user_code']}")

    interval = data.get("interval", 5)
    expires = time.time() + data["expires_in"]

    while time.time() < expires:
        time.sleep(interval)
        poll = {
            "code": data["device_code"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        r = requests.post(TOKEN_URL, json=poll)

        if r.status_code == 200:
            token_data = r.json()
            token_data["created_at"] = int(time.time())
            save_token(token_data)
            print("✅ Device flow completed")
            return token_data

        if r.status_code != 400:
            print(f"❌ Unexpected error: {r.status_code} {r.text}")
            return None

    print("❌ Device flow expired")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-flow", action="store_true",
                        help="Force device flow manually")
    parser.add_argument("--no-device-flow", action="store_true",
                        help="Disable device flow (for GitHub Actions)")
    args = parser.parse_args()

    token_data
