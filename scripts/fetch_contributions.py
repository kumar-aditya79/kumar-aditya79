from pathlib import Path
import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


USERNAME = "kumar-aditya79"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT_FILE = Path("data/contributions.json")


def fetch_page():
    print(f"Fetching contributions for @{USERNAME}...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html):
    soup = BeautifulSoup(html, "html.parser")

    days = []

    # GitHub contribution cells
    for rect in soup.select("td.ContributionCalendar-day"):
        date = rect.get("data-date")
        count_text = rect.get("data-level")

        if date and count_text is not None:
            days.append({
                "date": date,
                "level": int(count_text),
            })

    # Fallback for newer GitHub markup
    if not days:
        for element in soup.select("[data-date][data-level]"):
            date = element.get("data-date")
            level = element.get("data-level")

            if date and level is not None:
                days.append({
                    "date": date,
                    "level": int(level),
                })

    return days


def calculate_stats(days):
    if not days:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
        }

    # GitHub levels:
    # 0 = no contributions
    # 1-4 = increasing contribution intensity

    total = 0

    for day in days:
        # We don't get the exact count from data-level,
        # so total is calculated from the aria-label when available
        pass

    # Build a date → level dictionary
    levels = {
        day["date"]: day["level"]
        for day in days
    }

    dates = sorted(levels.keys())

    # Current streak
    current_streak = 0

    for date in reversed(dates):
        if levels[date] > 0:
            current_streak += 1
        else:
            break

    # Longest streak
    longest_streak = 0
    streak = 0

    for date in dates:
        if levels[date] > 0:
            streak += 1
            longest_streak = max(
                longest_streak,
                streak
            )
        else:
            streak = 0

    # Best contribution level
    best_day = max(
        days,
        key=lambda x: x["level"]
    )

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
    }


def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    html = fetch_page()

    days = parse_contributions(html)

    print(f"Found {len(days)} contribution days.")

    if not days:
        print()
        print("WARNING: No contribution cells were found.")
        print("GitHub may have changed its HTML structure.")
        print()
        print("Open this URL in your browser:")
        print(URL)

    stats = calculate_stats(days)

    output = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("Done!")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()