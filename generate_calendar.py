import os
import requests
from datetime import datetime
from ics import Calendar, Event
import smtplib
from email.mime.text import MIMEText

def send_refresh_token_email(refresh_token: str):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    to_email = os.environ.get("REFRESH_TOKEN_TO")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, to_email]):
        print("Email configuration is incomplete, skipping sending refresh token email.")
        return

    subject = "New Trakt refresh token"
    body = f"Refresh token: {refresh_token}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

CLIENT_ID = os.environ["TRAKT_CLIENT_ID"]
CLIENT_SECRET = os.environ["TRAKT_CLIENT_SECRET"]
ACCESS_TOKEN = os.environ["TRAKT_ACCESS_TOKEN"]
REFRESH_TOKEN = os.environ["TRAKT_REFRESH_TOKEN"]

def refresh_access_token():
    url = "https://api.trakt.tv/oauth/token"
    payload = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "refresh_token"
    }
    r = requests.post(url, json=payload)

    print("TRAKT_REFRESH_STATUS:", r.status_code)
    print("TRAKT_REFRESH_BODY:", r.text)
    r.raise_for_status()

    data = r.json()
    print("DEBUG_REFRESH_TOKEN:", data.get("refresh_token"))
    
    send_refresh_token_email(data["refresh_token"])
    
    return data["access_token"], data["refresh_token"]

START_DATE = datetime.utcnow().strftime("%Y-%m-%d")
DAYS = 120

url = f"https://api.trakt.tv/calendars/my/shows/{START_DATE}/{DAYS}"
headers = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": CLIENT_ID,
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

resp = requests.get(url, headers=headers)

if resp.status_code == 401:
    ACCESS_TOKEN, REFRESH_TOKEN = refresh_access_token()
    headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    resp = requests.get(url, headers=headers)

resp.raise_for_status()
data = resp.json()

cal = Calendar()
for item in data:
    show = item["show"]["title"]
    ep = item["episode"]["title"]
    season = item["episode"]["season"]
    number = item["episode"]["number"]
    first_aired = item["first_aired"]

    # vytvoření eventu
    event = Event()
    event.name = f"{show} S{season:02d}E{number:02d} - {ep}"
    event.begin = first_aired
    cal.events.add(event)

with open("tv_calendar.ics", "w", encoding="utf-8") as f:
    f.writelines(cal)
