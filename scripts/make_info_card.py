from pathlib import Path
import os
import html


OUTPUT_FILE = Path("info-card.svg")

WIDTH = 490
HEIGHT = 430

BACKGROUND = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"

GREEN = "#3fb950"
BLUE = "#58a6ff"
PURPLE = "#bc8cff"
ORANGE = "#d29922"


def esc(text):
    return html.escape(str(text))


def text(x, y, value, color=TEXT, size=13, weight="normal"):
    return (
        f'<text x="{x}" y="{y}" '
        f'fill="{color}" '
        f'font-size="{size}px" '
        f'font-family="monospace" '
        f'font-weight="{weight}">'
        f'{esc(value)}</text>'
    )


def main():

    static = os.getenv("STATIC") == "1"

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    svg.append(f"""
<style>

.card-line {{
    opacity: 0;
    animation: fadeIn 0.45s ease forwards;
}}

@keyframes fadeIn {{
    from {{
        opacity: 0;
        transform: translateX(-8px);
    }}

    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

</style>
""")

    # Card background
    svg.append(
        f'<rect x="0" y="0" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'rx="8" '
        f'fill="{BACKGROUND}" '
        f'stroke="{BORDER}"/>'
    )

    # Terminal title bar
    svg.append(
        f'<circle cx="18" cy="18" r="5" fill="#ff5f56"/>'
    )

    svg.append(
        f'<circle cx="36" cy="18" r="5" fill="#ffbd2e"/>'
    )

    svg.append(
        f'<circle cx="54" cy="18" r="5" fill="#27c93f"/>'
    )

    svg.append(
        text(
            75,
            22,
            "kumar-aditya79@github",
            MUTED,
            11
        )
    )

    # Main command
    svg.append(
        text(
            22,
            55,
            "$ whoami",
            GREEN,
            12
        )
    )

    # Profile information
    rows = [
        ("Role", "Aspiring Data Engineer", BLUE),
        ("Focus", "Data Engineering & Big Data", PURPLE),
        ("Stack", "Python · SQL · PySpark", BLUE),
        ("Cloud", "Azure · Databricks", ORANGE),
        ("Data", "ETL · Data Pipelines", GREEN),
        ("Tools", "Git · GitHub · Docker", BLUE),
    ]

    start_y = 88
    row_gap = 34

    for index, (key, value, color) in enumerate(rows):

        y = start_y + index * row_gap

        delay = index * 0.10

        if static:
            delay = 0

        svg.append(
            f'<g class="card-line" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        svg.append(
            text(
                25,
                y,
                f"{key}:",
                color,
                12,
                "bold"
            )
        )

        svg.append(
            text(
                105,
                y,
                value,
                TEXT,
                12
            )
        )

        svg.append("</g>")

    # Separator
    separator_y = 300

    svg.append(
        f'<line x1="22" y1="{separator_y}" '
        f'x2="{WIDTH - 22}" y2="{separator_y}" '
        f'stroke="{BORDER}"/>'
    )

    # Highlights heading
    svg.append(
        text(
            22,
            328,
            "$ highlights",
            GREEN,
            12
        )
    )

    highlights = [
        "Building scalable data pipelines",
        "Learning Cloud & Big Data",
        "Exploring Databricks",
    ]

    highlight_start = 355
    highlight_gap = 23

    for index, value in enumerate(highlights):

        y = (
            highlight_start
            + index * highlight_gap
        )

        delay = (
            (len(rows) + index)
            * 0.10
        )

        if static:
            delay = 0

        svg.append(
            f'<g class="card-line" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        svg.append(
            text(
                30,
                y,
                f"→ {value}",
                TEXT,
                11
            )
        )

        svg.append("</g>")

    # Final command
    final_y = 420

    svg.append(
        text(
            22,
            final_y,
            '$ echo "Keep building"',
            GREEN,
            11
        )
    )

    svg.append("</svg>")

    OUTPUT_FILE.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print("Done!")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
