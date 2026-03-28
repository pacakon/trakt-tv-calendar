import requests
import json
from datetime import datetime, timedelta

TOKEN_FILE = "token_state.json"
CALENDAR_FILE = "calendar.ics"

TRAKT_API_URL = "https://api.trakt.tv"
HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
}


def load_access_token():
    """Load access token from token_state.json"""
    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            return data["access_token"]
    except Exception:
        print("❌ Could not load access token from token_state.json")
        return None


def fetch_calendar(access_token):
    """Fetch user's Trakt calendar"""
    print("📅 Fetching Trakt calendar...")

    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {access_token}"
    headers["trakt-api-key"] = "c3f3f4f4c6f5c4e4b4e4a4d4c4b4a4d4"

    today = datetime.utcnow().strftime("%Y-%m-%d")
    days = 30  # how many days ahead

    url = f"{TRAKT_API_URL}/calendars/my/shows/{today}/{days}"

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"❌ Calendar fetch failed: {r.status_code} {r.text}")
        return None

    print("✅ Calendar fetched successfully")
    return r.json()


def generate_ics(events):
    """Generate ICS file from Trakt events"""
    print("📝 Generating ICS file...")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//Trakt Calendar//EN",
    ]

    for item in events:
        show = item.get("show", {})
        episode = item.get("episode", {})
        first_aired = episode.get("first_aired")

        if not first_aired:
            continue

        dt = datetime.fromisoformat(first_aired.replace("Z", "+00:00"))
        dt_str = dt.strftime("%Y%m%dT%H%M%SZ")

        title = f"{show.get('title', 'Unknown Show')} - S{episode.get('season', 0):02d}E{episode.get('number', 0):02d}"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{show.get('ids', {}).get('trakt', '')}-{episode.get('ids', {}).get('trakt', '')}",
            f"DTSTAMP:{dt_str}",
            f"DTSTART:{dt_str}",
            f"SUMMARY:{title}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    with open(CALENDAR_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"📂 Saved: {CALENDAR_FILE}")


def main():
    access_token = load_access_token()
    if not access_token:
        print("⛔ No access token available. Exiting.")
        return

    events = fetch_calendar(access_token)
    if not events:
        print("⛔ No events fetched. Exiting.")
        return

    generate_ics(events)
    print("🎉 Calendar generation complete!")


if __name__ == "__main__":
    main()
