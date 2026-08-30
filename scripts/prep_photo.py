from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session


# Input/output files
INPUT_FILE = Path("source-photo.jpg")
OUTPUT_FILE = Path("source-prepped.png")


def main():
    # Check that the input photo exists
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} was not found.")
        print("Make sure source-photo.jpg is in the project root folder.")
        sys.exit(1)

    print("Loading photo...")

    # Open the image
    image = Image.open(INPUT_FILE).convert("RGBA")

    # Remove the background using the lighter U2Net model
    print("Removing background...")

    session = new_session("u2net")
    foreground = remove(image, session=session)

    # Convert to OpenCV format
    image_np = np.array(foreground)

    # Separate RGB and alpha channels
    rgb = image_np[:, :, :3]
    alpha = image_np[:, :, 3]

    # Create a pure white background
    white_background = np.full_like(rgb, 255)

    # Composite the subject onto white
    alpha_float = alpha.astype(np.float32) / 255.0

    composited = (
        rgb.astype(np.float32) * alpha_float[:, :, None]
        + white_background.astype(np.float32)
        * (1 - alpha_float[:, :, None])
    )

    composited = np.clip(composited, 0, 255).astype(np.uint8)

    # Convert to grayscale
    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)

    # Improve local contrast using CLAHE
    print("Improving contrast...")

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Save the processed image
    cv2.imwrite(str(OUTPUT_FILE), enhanced)

    print()
    print("Done!")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()