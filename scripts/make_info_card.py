from pathlib import Path
import html


OUTPUT_FILE = Path("info-card.svg")

USERNAME = "kumar-aditya79"

WIDTH = 490
HEIGHT = 470

BACKGROUND = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"

GREEN = "#3fb950"
BLUE = "#58a6ff"


def esc(value):
    return html.escape(str(value))


def make_text(
    x,
    y,
    value,
    color=TEXT,
    size=12,
    weight="normal"
):
    return (
        f'<text x="{x}" y="{y}" '
        f'fill="{color}" '
        f'font-size="{size}px" '
        f'font-family="monospace" '
        f'font-weight="{weight}">'
        f'{esc(value)}</text>'
    )


def main():

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    # ------------------------------------------
    # Animation
    # ------------------------------------------

    svg.append("""
<style>

.line {
    opacity: 0;
    animation: fadeIn 0.55s ease forwards;
}

@keyframes fadeIn {

    from {
        opacity: 0;
        transform: translateX(-10px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }

}

</style>
""")

    # Background
    svg.append(
        f'<rect x="0" y="0" '
        f'width="{WIDTH}" '
        f'height="{HEIGHT}" '
        f'rx="8" '
        f'fill="{BACKGROUND}" '
        f'stroke="{BORDER}"/>'
    )

    # Terminal buttons
    svg.append(
        '<circle cx="18" cy="18" r="5" fill="#ff5f56"/>'
    )

    svg.append(
        '<circle cx="36" cy="18" r="5" fill="#ffbd2e"/>'
    )

    svg.append(
        '<circle cx="54" cy="18" r="5" fill="#27c93f"/>'
    )

    # Username
    svg.append(
        make_text(
            75,
            22,
            f"{USERNAME}@github",
            MUTED,
            11
        )
    )

    # whoami command
    svg.append(
        make_text(
            22,
            55,
            "$ whoami",
            GREEN,
            12
        )
    )

    # ------------------------------------------
    # Profile information
    # ------------------------------------------

    info = [
        ("Role", "Aspiring Data Engineer"),
        ("Languages", "Python · SQL · C++"),
        ("Big Data", "PySpark · Apache Spark"),
        ("Cloud", "Azure · Databricks"),
        ("Data", "ETL · Data Pipelines"),
        ("Database", "MySQL · MongoDB"),
    ]

    start_y = 88
    row_gap = 34

    for index, (key, value) in enumerate(info):

        y = start_y + index * row_gap
        delay = index * 0.12

        svg.append(
            f'<g class="line" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        svg.append(
            make_text(
                25,
                y,
                key,
                BLUE,
                12,
                "bold"
            )
        )

        svg.append(
            make_text(
                120,
                y,
                value,
                TEXT,
                12
            )
        )

        svg.append("</g>")

    # ------------------------------------------
    # Separator
    # ------------------------------------------

    separator_y = 300

    svg.append(
        f'<line x1="22" y1="{separator_y}" '
        f'x2="{WIDTH - 22}" '
        f'y2="{separator_y}" '
        f'stroke="{BORDER}"/>'
    )

    # ------------------------------------------
    # Highlights
    # ------------------------------------------

    svg.append(
        f'<g class="line" '
        f'style="animation-delay:0.85s">'
    )

    svg.append(
        make_text(
            22,
            328,
            "$ highlights",
            GREEN,
            12
        )
    )

    svg.append("</g>")

    highlights = [
        "Building scalable data pipelines",
        "Learning Cloud & Big Data",
        "Exploring Databricks",
    ]

    highlight_y = 358
    highlight_gap = 25

    for index, item in enumerate(highlights):

        y = highlight_y + index * highlight_gap
        delay = 1.0 + index * 0.15

        svg.append(
            f'<g class="line" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        svg.append(
            make_text(
                30,
                y,
                f"→ {item}",
                TEXT,
                11
            )
        )

        svg.append("</g>")

    # ------------------------------------------
    # Final command
    # ------------------------------------------

    svg.append(
        f'<g class="line" '
        f'style="animation-delay:1.55s">'
    )

    svg.append(
        make_text(
            22,
            445,
            '$ echo "Keep building"',
            GREEN,
            11
        )
    )

    svg.append("</g>")

    svg.append("</svg>")

    OUTPUT_FILE.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print("Done!")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
