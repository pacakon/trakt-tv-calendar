import os
import requests
from datetime import datetime
from ics import Calendar, Event

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
