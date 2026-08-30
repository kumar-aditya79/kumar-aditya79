from pathlib import Path
import html
import math

import numpy as np
from PIL import Image


INPUT_FILE = Path("source-prepped.png")
OUTPUT_FILE = Path("avi-ascii.svg")

# ASCII characters from light → dark
RAMP = " .`:-=+*cs#%@"

# Character grid
COLUMNS = 100

# Animation settings
ROW_DURATION = 0.12
CURSOR_WIDTH = 18


def brightness_to_char(value):
    """Convert brightness (0-255) to an ASCII character."""
    index = int((255 - value) / 255 * (len(RAMP) - 1))
    return RAMP[index]


def load_image():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} was not found. "
            "Run prep_photo.py first."
        )

    image = Image.open(INPUT_FILE).convert("L")

    width, height = image.size

    # Characters are taller than they are wide, so compensate
    # for character aspect ratio.
    char_aspect = 0.5

    rows = max(
        1,
        int(height / width * COLUMNS * char_aspect)
    )

    image = image.resize(
        (COLUMNS, rows),
        Image.Resampling.LANCZOS
    )

    return np.array(image)


def build_ascii(image):
    rows = []

    for row in image:
        text = "".join(
            brightness_to_char(pixel)
            for pixel in row
        )
        rows.append(text)

    return rows


def create_svg(rows):
    rows_count = len(rows)

    char_width = 8
    char_height = 14

    width = COLUMNS * char_width
    height = rows_count * char_height

    escaped_rows = [
        html.escape(row)
        for row in rows
    ]

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    svg.append("""
    <style>
        .ascii {
            font-family: "Courier New", monospace;
            font-size: 14px;
            font-weight: 400;
            fill: #b8b8b8;
        }

        .cursor {
            fill: #b8b8b8;
            opacity: 0.9;
        }

        @keyframes reveal {
            from {
                transform: translateX(-100%);
            }
            to {
                transform: translateX(0);
            }
        }

        .reveal {
            animation-name: reveal;
            animation-timing-function: linear;
            animation-fill-mode: forwards;
        }
    </style>
    """)

    # Define clipping paths for every row.
    svg.append("<defs>")

    for i in range(rows_count):
        y = i * char_height

        svg.append(
            f'<clipPath id="clip-{i}">'
            f'<rect x="0" y="{y}" '
            f'width="{width}" height="{char_height}" />'
            f'</clipPath>'
        )

    svg.append("</defs>")

    # Draw each row.
    for i, row in enumerate(escaped_rows):
        y = (i + 1) * char_height - 2

        delay = i * ROW_DURATION

        svg.append(
            f'<g clip-path="url(#clip-{i})" '
            f'style="animation-delay:{delay:.2f}s">'
        )

        svg.append(
            f'<text class="ascii" '
            f'x="0" y="{y}">{row}</text>'
        )

        svg.append("</g>")

    # Cursor-like wipe.
    total_duration = rows_count * ROW_DURATION

    svg.append(
        f"""
        <rect
            class="cursor"
            x="0"
            y="0"
            width="{CURSOR_WIDTH}"
            height="{height}"
            opacity="0">
            <animate
                attributeName="x"
                from="0"
                to="{width}"
                dur="{total_duration:.2f}s"
                fill="freeze"
            />
            <animate
                attributeName="opacity"
                values="0;1;1;0"
                keyTimes="0;0.02;0.95;1"
                dur="{total_duration:.2f}s"
                fill="freeze"
            />
        </rect>
        """
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():
    print("Loading prepared image...")

    image = load_image()

    print(
        f"Creating ASCII grid: "
        f"{image.shape[1]} × {image.shape[0]}"
    )

    rows = build_ascii(image)

    print("Generating animated SVG...")

    svg = create_svg(rows)

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("Done!")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()