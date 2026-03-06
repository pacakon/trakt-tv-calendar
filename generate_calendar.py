import os
import requests

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
    r.raise_for_status()

    data = r.json()
    return data["access_token"], data["refresh_token"]
import requests
from datetime import datetime
from ics import Calendar, Event
import os

CLIENT_ID = os.environ["TRAKT_CLIENT_ID"]
ACCESS_TOKEN = os.environ["TRAKT_ACCESS_TOKEN"]

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
    airdate = item["first_aired"]

    e = Event()
    e.name = f"{show} S{season:02}E{number:02} – {ep}"
    e.begin = airdate
    cal.events.add(e)

os.makedirs("docs", exist_ok=True)

with open("docs/premieres.ics", "w") as f:
    f.writelines(cal)

print("Calendar generated.")
