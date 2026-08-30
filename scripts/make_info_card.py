from pathlib import Path
import os
import html


OUTPUT_FILE = Path("info-card.svg")


# --------------------------------------------------
# Customize your profile information here
# --------------------------------------------------

USERNAME = "kumar-aditya79"

INFO = [
    ("Role", "Aspiring Data Engineer"),
    ("Languages", "Python · SQL · C++"),
    ("Big Data", "PySpark · Apache Spark"),
    ("Cloud", "Azure · Databricks"),
    ("Data", "ETL · Data Pipelines"),
    ("Database", "MySQL · MongoDB"),
]

HIGHLIGHTS = [
    "Building scalable data pipelines",
    "Learning Cloud & Big Data",
    "Exploring Azure & Databricks",
]


# --------------------------------------------------
# SVG settings
# --------------------------------------------------

WIDTH = 490
HEIGHT = 390

BACKGROUND = "#0d1117"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
BORDER = "#30363d"


def escape(text):
    return html.escape(str(text))


def create_svg():
    lines = []

    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    )

    # --------------------------------------------------
    # Animation
    # --------------------------------------------------

    lines.append("""
    <style>

        .terminal {
            font-family:
                "JetBrains Mono",
                "Cascadia Code",
                "Courier New",
                monospace;
        }

        .fade {
            opacity: 0;
            animation: fadeIn 0.6s ease forwards;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(6px);
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

    lines.append(
        f'<rect width="{WIDTH}" height="{HEIGHT}" '
        f'rx="12" fill="{BACKGROUND}" '
        f'stroke="{BORDER}" stroke-width="1"/>'
    )

    # --------------------------------------------------
    # Terminal header
    # --------------------------------------------------

    lines.append(
        '<circle cx="20" cy="20" r="5" fill="#ff5f56"/>'
    )

    lines.append(
        '<circle cx="38" cy="20" r="5" fill="#ffbd2e"/>'
    )

    lines.append(
        '<circle cx="56" cy="20" r="5" fill="#27c93f"/>'
    )

    lines.append(
        f'<text x="75" y="25" '
        f'fill="{MUTED}" font-size="12" '
        f'class="terminal">'
        f'{escape(USERNAME)}@github'
        f'</text>'
    )

    # --------------------------------------------------
    # Command
    # --------------------------------------------------

    lines.append(
        f'<text x="25" y="62" '
        f'fill="{GREEN}" font-size="14" '
        f'class="terminal">'
        f'$ whoami'
        f'</text>'
    )

    # --------------------------------------------------
    # Information rows
    # --------------------------------------------------

    y = 92

    for index, (key, value) in enumerate(INFO):

        delay = 0.3 + index * 0.15

        lines.append(
            f'<g class="fade" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        lines.append(
            f'<text x="25" y="{y}" '
            f'fill="{ACCENT}" '
            f'font-size="13" '
            f'font-weight="bold" '
            f'class="terminal">'
            f'{escape(key)}'
            f'</text>'
        )

        lines.append(
            f'<text x="125" y="{y}" '
            f'fill="{TEXT}" '
            f'font-size="13" '
            f'class="terminal">'
            f'{escape(value)}'
            f'</text>'
        )

        lines.append("</g>")

        y += 32

    # --------------------------------------------------
    # Highlights heading
    # --------------------------------------------------

    delay = 0.3 + len(INFO) * 0.15

    lines.append(
        f'<g class="fade" '
        f'style="animation-delay:{delay:.2f}s">'
    )

    lines.append(
        f'<text x="25" y="{y + 10}" '
        f'fill="{GREEN}" '
        f'font-size="14" '
        f'class="terminal">'
        f'$ highlights'
        f'</text>'
    )

    lines.append("</g>")

    y += 40

    # --------------------------------------------------
    # Highlight items
    # --------------------------------------------------

    for index, highlight in enumerate(HIGHLIGHTS):

        delay = 1.3 + index * 0.18

        lines.append(
            f'<g class="fade" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        lines.append(
            f'<text x="30" y="{y}" '
            f'fill="{MUTED}" '
            f'font-size="12" '
            f'class="terminal">'
            f'→ {escape(highlight)}'
            f'</text>'
        )

        lines.append("</g>")

        y += 25

    # --------------------------------------------------
    # Bottom command
    # --------------------------------------------------

    lines.append(
        f'<text x="25" y="{HEIGHT - 18}" '
        f'fill="{GREEN}" '
        f'font-size="12" '
        f'class="terminal">'
        f'$ echo "keep building..."'
        f'</text>'
    )

    lines.append("</svg>")

    return "\n".join(lines)


def main():

    print("Generating info card...")

    svg = create_svg()

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("Done!")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()