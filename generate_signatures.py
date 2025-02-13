import csv
import os
from PIL import (
    Image,
    ImageDraw,
    ImageFont
)

# Configuration
OUTPUT_DIRECTORY = 'output'
LOGO_DIRECTORY = 'logos'
MAX_WIDTH = 1200
MAX_HEIGHT = 400
FONT_NAME = 'Roboto'
FONT_SIZE = 24
NAME_LINE_HEIGHT = 100
LINE_HEIGHT = 30
MARGIN = 20
SEPARATOR_COLOR = (0, 0, 0, 255)
TEXT_COLOR = (0, 0, 0, 255)

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

# Load Roboto font
try:
    name_font = ImageFont.truetype(FONT_NAME + '.ttf', 60)
    font = ImageFont.truetype(FONT_NAME + '.ttf', FONT_SIZE)
except OSError:
    name_font = ImageFont.load_default()
    font = ImageFont.load_default()
    print("Warning: Roboto font not found. Using default font.")


def create_signature(row):
    # Create image with transparent background
    img = Image.new(
        'RGBA',
        (MAX_WIDTH, MAX_HEIGHT),
        (0, 0, 0, 0)
    )
    draw = ImageDraw.Draw(img)

    # Load logo
    logo_path = os.path.join(LOGO_DIRECTORY, row['Logo Filename'])
    if not os.path.exists(logo_path):
        print(f"Warning: Logo '{logo_path}' not found. Skipping.")
        return

    logo = Image.open(logo_path)

    # Calculate logo dimensions to fit max height while preserving ratio
    aspect_ratio = logo.width / logo.height
    # Maximum height for logo
    logo_height = MAX_HEIGHT - 2 * MARGIN
    logo_width = int(aspect_ratio * logo_height)

    # Ensure logo doesn't exceed available width
    if logo_width > (MAX_WIDTH // 3):
        logo_width = MAX_WIDTH // 3
        logo_height = int((logo_width / aspect_ratio) + 0.5)

    logo = logo.resize((logo_width, logo_height), Image.BICUBIC)
    img.paste(logo, (MARGIN, MARGIN))

    # Enable font features and anti-aliasing for better text rendering
    font_features = ['rlig', 'calt']
    text_smoothness_params = {
        'smooth': True,
        'font_features': font_features
    }

    # Draw separator
    separator_x = logo_width + MARGIN * 2
    draw.line(
        (separator_x, MARGIN, separator_x, MAX_HEIGHT - MARGIN),
        fill=SEPARATOR_COLOR,
        width=1
    )

    # Prepare text lines
    lines = [
        row['Name'],
        row['Position'],
        row['Email Address'],
        row['Phone Number'],
        row['Mailing Address']
    ]

    # Calculate text area dimensions
    text_area_x = separator_x + MARGIN
    text_area_height = MAX_HEIGHT - 2 * MARGIN

    # Calculate total height of all text
    total_text_height = NAME_LINE_HEIGHT + (len(lines) - 1) * LINE_HEIGHT

    # Calculate starting y position to center text vertically
    y = MARGIN + (text_area_height - total_text_height) // 2
    for line in lines:
        if y + LINE_HEIGHT > text_area_height:
            break
            
        # Add text shadow
        draw.text(
            (text_area_x + 1, y + 1),  # Offset for shadow
            line,
            fill=(0, 0, 0, 128),  # Semi-transparent black for shadow
            font=name_font if line == row['Name'] else font,
            **text_smoothness_params
        )
        
        if line == row['Name']:
            draw.text(
                (text_area_x, y),
                line,
                fill=TEXT_COLOR,
                font=name_font,
                **text_smoothness_params
            )
            y += NAME_LINE_HEIGHT
        else:
            draw.text(
                (text_area_x, y),
                line,
                fill=TEXT_COLOR,
                font=font,
                **text_smoothness_params
            )
            y += LINE_HEIGHT

    # Save image
    filename = f"{row['Name']}_signature.png"
    img.save(os.path.join(OUTPUT_DIRECTORY, filename))
    print(f"Signature generated: {filename}")


def main():
    with open('signatures.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create_signature(row)


if __name__ == "__main__":
    main()
