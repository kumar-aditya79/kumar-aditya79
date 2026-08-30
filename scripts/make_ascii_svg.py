from pathlib import Path
import html

import cv2
import numpy as np


INPUT_FILE = Path("source-prepped.png")
OUTPUT_FILE = Path("avi-ascii.svg")

RAMP = " .:-=+*#%@"

CHAR_WIDTH = 90
CHAR_ASPECT = 0.50

CHAR_WIDTH_PX = 5.2
LINE_HEIGHT = 8.5

TEXT_COLOR = "#c9d1d9"


def load_image():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} was not found."
        )

    image = cv2.imread(
        str(INPUT_FILE),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise RuntimeError(
            f"Could not read {INPUT_FILE}"
        )

    return image


def crop_to_subject(image):

    mask = image < 245

    ys, xs = np.where(mask)

    if len(xs) == 0:
        return image

    x1 = max(0, xs.min() - 10)
    x2 = min(image.shape[1], xs.max() + 11)

    y1 = max(0, ys.min() - 10)
    y2 = min(image.shape[0], ys.max() + 11)

    return image[y1:y2, x1:x2]


def resize_for_ascii(image):

    height, width = image.shape

    char_height = max(
        1,
        int(
            CHAR_WIDTH
            * height
            / width
            * CHAR_ASPECT
        )
    )

    return cv2.resize(
        image,
        (CHAR_WIDTH, char_height),
        interpolation=cv2.INTER_AREA
    )


def pixel_to_char(value):

    index = int(
        (255 - int(value))
        / 255
        * (len(RAMP) - 1)
    )

    index = max(
        0,
        min(index, len(RAMP) - 1)
    )

    return RAMP[index]


def make_ascii(image):

    rows = []

    for row in image:

        line = ""

        for pixel in row:
            line += pixel_to_char(pixel)

        rows.append(line.rstrip())

    while rows and not rows[0].strip():
        rows.pop(0)

    while rows and not rows[-1].strip():
        rows.pop()

    return rows


def escape_xml(text):
    return html.escape(text)


def create_svg(rows):

    if not rows:
        raise RuntimeError(
            "ASCII conversion produced no output."
        )

    max_chars = max(
        len(row)
        for row in rows
    )

    width = int(
        max_chars * CHAR_WIDTH_PX
    ) + 60

    height = int(
        len(rows) * LINE_HEIGHT
    ) + 60

    portrait_top = 35

    portrait_height = (
        len(rows) * LINE_HEIGHT
    )

    # Total duration of the complete scan
    SCAN_DURATION = 4.0

    svg = []

    # ==================================================
    # SVG
    # ==================================================

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" '
        f'height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    # ==================================================
    # DEFINITIONS
    # ==================================================

    svg.append("""
<defs>

    <filter
        id="scanGlow"
        x="-50%"
        y="-500%"
        width="200%"
        height="1100%"
    >

        <feGaussianBlur
            stdDeviation="4"
            result="blur"
        />

        <feMerge>

            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>

        </feMerge>

    </filter>

</defs>
""")

    # ==================================================
    # CSS
    # ==================================================

    svg.append(f"""
<style>

.ascii {{
    font-family:
        "Cascadia Mono",
        "Consolas",
        "Courier New",
        monospace;

    font-size: 7px;
    font-weight: 500;
    letter-spacing: 0;
}}


/* ==============================================
   LINE-BY-LINE REVEAL
   ============================================== */

.ascii-row {{

    opacity: 0;

    animation:
        revealRow {SCAN_DURATION}s
        linear forwards;

}}


@keyframes revealRow {{

    0% {{
        opacity: 0;
    }}

    5% {{
        opacity: 0;
    }}

    100% {{
        opacity: 1;
    }}

}}


/* ==============================================
   GREEN LASER
   Runs ONLY ONCE
   ============================================== */

.scanner {{

    animation:
        scanDown {SCAN_DURATION}s
        linear forwards;

}}


@keyframes scanDown {{

    0% {{
        transform:
            translateY(0px);

        opacity: 1;
    }}

    5% {{
        opacity: 1;
    }}

    95% {{
        opacity: 1;
    }}

    100% {{
        transform:
            translateY({portrait_height}px);

        opacity: 0;
    }}

}}


/* ==============================================
   SCANNER GLOW
   ============================================== */

.scanner-glow {{

    animation:
        scanDown {SCAN_DURATION}s
        linear forwards;

}}

</style>
""")

    # ==================================================
    # BACKGROUND
    # ==================================================

    svg.append(
        f'<rect '
        f'x="0" '
        f'y="0" '
        f'width="{width}" '
        f'height="{height}" '
        f'rx="8" '
        f'fill="#0d1117"/>'
    )

    # ==================================================
    # TERMINAL COMMAND
    # ==================================================

    svg.append(
        '<text '
        'x="20" '
        'y="18" '
        'fill="#3fb950" '
        'font-size="10px" '
        'font-family="monospace">'
        '$ cat avi-ascii.svg'
        '</text>'
    )

    # ==================================================
    # ASCII PORTRAIT
    # ==================================================

    total_rows = len(rows)

    for index, row in enumerate(rows):

        row_width = (
            len(row)
            * CHAR_WIDTH_PX
        )

        x = (
            width
            - row_width
        ) / 2

        y = (
            portrait_top
            + index
            * LINE_HEIGHT
        )

        # Each row appears as the scanner
        # reaches approximately that row.

        delay = (
            index
            / max(total_rows - 1, 1)
            * SCAN_DURATION
        )

        svg.append(
            f'<text '
            f'x="{x:.2f}" '
            f'y="{y:.2f}" '
            f'fill="{TEXT_COLOR}" '
            f'class="ascii ascii-row" '
            f'style="animation-delay:{delay:.3f}s">'
            f'{escape_xml(row)}'
            f'</text>'
        )

    # ==================================================
    # GREEN LASER
    # ==================================================

    scanner_y = portrait_top - 5

    # Glow
    svg.append(
        f'<rect '
        f'x="0" '
        f'y="{scanner_y}" '
        f'width="{width}" '
        f'height="8" '
        f'rx="4" '
        f'fill="#39d353" '
        f'opacity="0.25" '
        f'filter="url(#scanGlow)" '
        f'class="scanner-glow"/>'
    )

    # Main laser
    svg.append(
        f'<rect '
        f'x="0" '
        f'y="{scanner_y}" '
        f'width="{width}" '
        f'height="2" '
        f'rx="1" '
        f'fill="#39d353" '
        f'opacity="1" '
        f'filter="url(#scanGlow)" '
        f'class="scanner"/>'
    )

    # ==================================================
    # FOOTER
    # ==================================================

    svg.append(
        f'<text '
        f'x="20" '
        f'y="{height - 15}" '
        f'fill="#3fb950" '
        f'font-size="9px" '
        f'font-family="monospace">'
        f'github.com/kumar-aditya79'
        f'</text>'
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():

    print("Loading processed photo...")

    image = load_image()

    print(
        f"Original image: "
        f"{image.shape[1]} × "
        f"{image.shape[0]}"
    )

    print("Finding subject...")

    image = crop_to_subject(image)

    print(
        f"Cropped image: "
        f"{image.shape[1]} × "
        f"{image.shape[0]}"
    )

    print("Converting to ASCII...")

    image = resize_for_ascii(image)

    rows = make_ascii(image)

    print(
        f"ASCII size: "
        f"{len(rows)} rows × "
        f"{CHAR_WIDTH} columns"
    )

    print("Generating scan + reveal animation...")

    svg = create_svg(rows)

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