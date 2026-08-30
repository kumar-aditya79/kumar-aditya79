from pathlib import Path
import json
from datetime import datetime, timedelta
import html


INPUT_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("contrib-heatmap.svg")

USERNAME = "kumar-aditya79"

# GitHub-style colors
PALETTE = [
    "#161b22",  # 0 contributions
    "#0e4429",  # level 1
    "#006d32",  # level 2
    "#26a641",  # level 3
    "#39d353",  # level 4
]

# Layout
CELL_SIZE = 13
CELL_GAP = 3
CELL_STEP = CELL_SIZE + CELL_GAP

LEFT_MARGIN = 35
TOP_MARGIN = 30

WEEKS = 53
DAYS = 7

WIDTH = LEFT_MARGIN + WEEKS * CELL_STEP + 20
HEIGHT = TOP_MARGIN + DAYS * CELL_STEP + 55

ANIMATION_DELAY = 0.025


def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} was not found. "
            "Run fetch_contributions.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_grid(days):
    """
    Convert contribution data into a 53-week × 7-day grid.
    """

    levels = {
        item["date"]: item["level"]
        for item in days
    }

    if not levels:
        return []

    # Use the latest available date
    latest_date = max(
        datetime.strptime(date, "%Y-%m-%d").date()
        for date in levels
    )

    # Go back roughly one year
    start_date = latest_date - timedelta(days=364)

    # Move start backward to Sunday
    start_date -= timedelta(
        days=(start_date.weekday() + 1) % 7
    )

    grid = []

    for week in range(WEEKS):

        week_data = []

        for day in range(DAYS):

            current_date = (
                start_date
                + timedelta(days=week * 7 + day)
            )

            date_string = current_date.isoformat()

            level = levels.get(
                date_string,
                0
            )

            week_data.append(
                {
                    "date": date_string,
                    "level": level,
                }
            )

        grid.append(week_data)

    return grid


def create_svg(grid):
    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    # --------------------------------------------------
    # CSS animation
    # --------------------------------------------------

    svg.append("""
    <style>

        .terminal {
            font-family:
                "JetBrains Mono",
                "Cascadia Code",
                "Courier New",
                monospace;
        }

        .cell {
            opacity: 0;
            animation:
                appear 0.45s ease forwards;
        }

        @keyframes appear {

            from {
                opacity: 0;
                transform: translateY(-8px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }

        }

    </style>
    """)

    # --------------------------------------------------
    # Background
    # --------------------------------------------------

    svg.append(
        f'<rect width="{WIDTH}" '
        f'height="{HEIGHT}" '
        f'rx="10" '
        f'fill="#0d1117"/>'
    )

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    svg.append(
        f'<text x="20" y="20" '
        f'fill="#3fb950" '
        f'font-size="11" '
        f'class="terminal">'
        f'$ contributions --user {html.escape(USERNAME)}'
        f'</text>'
    )

    # --------------------------------------------------
    # Contribution cells
    # --------------------------------------------------

    animation_index = 0

    for week_index, week in enumerate(grid):

        for day_index, cell in enumerate(week):

            x = (
                LEFT_MARGIN
                + week_index * CELL_STEP
            )

            y = (
                TOP_MARGIN
                + day_index * CELL_STEP
            )

            level = cell["level"]

            color = PALETTE[
                min(level, len(PALETTE) - 1)
            ]

            delay = animation_index * ANIMATION_DELAY

            svg.append(
                f'<rect '
                f'x="{x}" '
                f'y="{y}" '
                f'width="{CELL_SIZE}" '
                f'height="{CELL_SIZE}" '
                f'rx="3" '
                f'fill="{color}" '
                f'class="cell" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>'
                f'{html.escape(cell["date"])} '
                f'· level {level}'
                f'</title>'
                f'</rect>'
            )

            animation_index += 1

    # --------------------------------------------------
    # Legend
    # --------------------------------------------------

    legend_y = TOP_MARGIN + DAYS * CELL_STEP + 12

    svg.append(
        f'<text x="{LEFT_MARGIN}" '
        f'y="{legend_y + 11}" '
        f'fill="#8b949e" '
        f'font-size="10" '
        f'class="terminal">'
        f'Less'
        f'</text>'
    )

    legend_start = LEFT_MARGIN + 35

    for index, color in enumerate(PALETTE):

        x = (
            legend_start
            + index * CELL_STEP
        )

        svg.append(
            f'<rect '
            f'x="{x}" '
            f'y="{legend_y}" '
            f'width="{CELL_SIZE}" '
            f'height="{CELL_SIZE}" '
            f'rx="3" '
            f'fill="{color}"/>'
        )

    more_x = (
        legend_start
        + len(PALETTE) * CELL_STEP
        + 5
    )

    svg.append(
        f'<text x="{more_x}" '
        f'y="{legend_y + 11}" '
        f'fill="#8b949e" '
        f'font-size="10" '
        f'class="terminal">'
        f'More'
        f'</text>'
    )

    # --------------------------------------------------
    # Footer
    # --------------------------------------------------

    svg.append(
        f'<text x="{LEFT_MARGIN}" '
        f'y="{HEIGHT - 8}" '
        f'fill="#8b949e" '
        f'font-size="9" '
        f'class="terminal">'
        f'github.com/{html.escape(USERNAME)}'
        f'</text>'
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():

    print("Loading contribution data...")

    data = load_data()

    days = data.get(
        "days",
        []
    )

    print(
        f"Loaded {len(days)} contribution days."
    )

    print("Building contribution grid...")

    grid = create_grid(days)

    print("Generating animated heatmap...")

    svg = create_svg(grid)

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("Done!")
    print(
        f"Created: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()