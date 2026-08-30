from pathlib import Path
import json
import os
from datetime import datetime, timedelta

import requests


USERNAME = "kumar-aditya79"
OUTPUT_FILE = Path("data/contributions.json")

GRAPHQL_URL = "https://api.github.com/graphql"


def fetch_contributions():
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not set. "
            "Set it in PowerShell before running this script."
        )

    today = datetime.utcnow().date()
    one_year_ago = today - timedelta(days=365)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $login) {
            contributionsCollection(
                from: $from
                to: $to
            ) {
                totalCommitContributions
                totalIssueContributions
                totalPullRequestContributions
                totalPullRequestReviewContributions
                restrictedContributionsCount

                contributionCalendar {
                    totalContributions

                    weeks {
                        contributionDays {
                            contributionCount
                            date
                            contributionLevel
                        }
                    }
                }
            }
        }
    }
    """

    variables = {
        "login": USERNAME,
        "from": f"{one_year_ago}T00:00:00Z",
        "to": f"{today}T23:59:59Z",
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    print(f"Fetching contributions for @{USERNAME}...")

    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": query,
            "variables": variables,
        },
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise RuntimeError(
            f"GitHub GraphQL error:\n{result['errors']}"
        )

    return result["data"]["user"]["contributionsCollection"]


def main():

    collection = fetch_contributions()

    calendar = collection["contributionCalendar"]

    days = []

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append({
                "date": day["date"],
                "count": day["contributionCount"],
                "level": day["contributionLevel"],
            })

    output = {
        "username": USERNAME,

        "generated_at": datetime.utcnow().isoformat() + "Z",

        "stats": {
            "total": calendar["totalContributions"],
            "commits": collection["totalCommitContributions"],
            "issues": collection["totalIssueContributions"],
            "pull_requests": collection[
                "totalPullRequestContributions"
            ],
            "reviews": collection[
                "totalPullRequestReviewContributions"
            ],
            "restricted": collection[
                "restrictedContributionsCount"
            ],
        },

        "days": days,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("===================================")
    print("GitHub contribution data fetched!")
    print("===================================")

    print(
        f"Total contributions: "
        f"{calendar['totalContributions']}"
    )

    print(
        f"Commit contributions: "
        f"{collection['totalCommitContributions']}"
    )

    print(
        f"Issue contributions: "
        f"{collection['totalIssueContributions']}"
    )

    print(
        f"Pull request contributions: "
        f"{collection['totalPullRequestContributions']}"
    )

    print(
        f"Pull request reviews: "
        f"{collection['totalPullRequestReviewContributions']}"
    )

    print()
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()