from pathlib import Path
import json
from datetime import datetime, timedelta
import html


INPUT_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("contrib-heatmap.svg")

USERNAME = "kumar-aditya79"

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

CELL_SIZE = 13
CELL_GAP = 3
CELL_STEP = CELL_SIZE + CELL_GAP

LEFT_MARGIN = 35
TOP_MARGIN = 30

WEEKS = 53
DAYS = 7

WIDTH = LEFT_MARGIN + WEEKS * CELL_STEP + 20
HEIGHT = TOP_MARGIN + DAYS * CELL_STEP + 75

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
    levels = {
        item["date"]: item
        for item in days
    }

    if not levels:
        return []

    latest_date = max(
        datetime.strptime(date, "%Y-%m-%d").date()
        for date in levels
    )

    start_date = latest_date - timedelta(days=364)

    # Move to Sunday
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

            contribution = levels.get(
                date_string,
                {
                    "date": date_string,
                    "count": 0,
                    "level": "NONE"
                }
            )

            week_data.append(contribution)

        grid.append(week_data)

    return grid


def get_level_number(level):
    level_map = {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4,

        # Support numeric levels too
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
    }

    if isinstance(level, int):
        return max(
            0,
            min(level, 4)
        )

    return level_map.get(
        str(level),
        0
    )


def create_svg(grid, total_contributions):

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

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

    # Background
    svg.append(
        f'<rect width="{WIDTH}" '
        f'height="{HEIGHT}" '
        f'rx="10" '
        f'fill="#0d1117"/>'
    )

    # Header
    svg.append(
        f'<text x="20" y="18" '
        f'fill="#3fb950" '
        f'font-size="10" '
        f'class="terminal">'
        f'$ contributions --user '
        f'{html.escape(USERNAME)}'
        f'</text>'
    )

    # Contribution count
    svg.append(
        f'<text x="20" y="29" '
        f'fill="#8b949e" '
        f'font-size="9" '
        f'class="terminal">'
        f'{total_contributions:,} contributions in the last year'
        f'</text>'
    )

    animation_index = 0

    # Contribution cells
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

            level = get_level_number(
                cell.get("level", "NONE")
            )

            color = PALETTE[
                min(
                    level,
                    len(PALETTE) - 1
                )
            ]

            count = cell.get(
                "count",
                0
            )

            date = cell.get(
                "date",
                ""
            )

            delay = (
                animation_index
                * ANIMATION_DELAY
            )

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
                f'{html.escape(date)} '
                f'· {count} contributions'
                f'</title>'
                f'</rect>'
            )

            animation_index += 1

    # Legend
    legend_y = (
        TOP_MARGIN
        + DAYS * CELL_STEP
        + 12
    )

    svg.append(
        f'<text x="{LEFT_MARGIN}" '
        f'y="{legend_y + 11}" '
        f'fill="#8b949e" '
        f'font-size="10" '
        f'class="terminal">'
        f'Less'
        f'</text>'
    )

    legend_start = (
        LEFT_MARGIN + 35
    )

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

    # Footer
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

    stats = data.get(
        "stats",
        {}
    )

    total_contributions = stats.get(
        "total",
        0
    )

    print(
        f"Loaded {len(days)} contribution days."
    )

    print(
        f"Total contributions: "
        f"{total_contributions}"
    )

    print("Building contribution grid...")

    grid = create_grid(days)

    print("Generating animated heatmap...")

    svg = create_svg(
        grid,
        total_contributions
    )

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