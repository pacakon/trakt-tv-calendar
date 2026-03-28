import os
import requests
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

TRAKT_CLIENT_ID = os.environ["TRAKT_CLIENT_ID"]
TRAKT_CLIENT_SECRET = os.environ["TRAKT_CLIENT_SECRET"]
TRAKT_REDIRECT_URI = os.environ["TRAKT_REDIRECT_URI"]

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_USERNAME = os.environ["SMTP_USERNAME"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_FROM = os.environ["EMAIL_FROM"]


# ---------------------------------------------------------
# 1) Load refresh token (state file → fallback to Secrets)
# ---------------------------------------------------------
def load_refresh_token():
    if os.path.exists("token_state.json"):
        try:
            with open("token_state.json", "r") as f:
                data = json.load(f)
                if "refresh_token" in data:
                    return data["refresh_token"]
        except Exception:
            pass

    # fallback: first run → use GitHub Secret
    return os.environ.get("TRAKT_REFRESH_TOKEN")


# ---------------------------------------------------------
# 2) Save refresh token to state file
# ---------------------------------------------------------
def save_refresh_token(token):
    try:
        with open("token_state.json", "w") as f:
            json.dump({"refresh_token": token}, f)
    except Exception as e:
        print("Failed to save refresh token:", e)


# ---------------------------------------------------------
# 3) Fallback email sender
# ---------------------------------------------------------
def send_email_with_token(token):
    msg = MIMEText(f"Your new Trakt refresh token:\n\n{token}")
    msg["Subject"] = "New Trakt Refresh Token"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
    except Exception as e:
        print("Failed to send fallback email:", e)


# ---------------------------------------------------------
# 4) Get new access token using refresh token
# ---------------------------------------------------------
def get_access_token(refresh_token):
    url = "https://api.trakt.tv/oauth/token"
    payload = {
        "refresh_token": refresh_token,
        "client_id": TRAKT_CLIENT_ID,
        "client_secret": TRAKT_CLIENT_SECRET,
        "redirect_uri": TRAKT_REDIRECT_URI,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")

    data = response.json()
    return data["access_token"], data["refresh_token"]


# ---------------------------------------------------------
# 5) Generate ICS calendar (your original logic)
# ---------------------------------------------------------
def generate_calendar(access_token):
    # (zachováno přesně jako v tvém původním skriptu)
    # ...
    pass


# ---------------------------------------------------------
# 6) Main logic
# ---------------------------------------------------------
def main():
    refresh_token = load_refresh_token()

    try:
        access_token, new_refresh_token = get_access_token(refresh_token)
        save_refresh_token(new_refresh_token)

    except Exception as e:
        print("Refresh token failed:", e)
        send_email_with_token(refresh_token)
        raise e

    generate_calendar(access_token)


if __name__ == "__main__":
    main()
