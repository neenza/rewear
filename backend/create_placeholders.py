#!/usr/bin/env python3
"""
Script to create actual PNG placeholder images for existing items.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(filename, text, size=(400, 400)):
    """Create a placeholder image with text"""
    # Create a new image with a light gray background
    img = Image.new('RGB', size, color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
    
    # Calculate text position to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='#666666', font=font)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created placeholder: {filename}")

def main():
    """Create placeholder images for existing items"""
    static_dir = "app/static/images"
    
    # Create placeholder images for the existing items
    placeholders = [
        ("item_1_primary.png", "Item 1"),
        ("item_2_primary.png", "Item 2"), 
        ("item_3_primary.png", "Item 3"),
        ("placeholder.png", "No Image")
    ]
    
    for filename, text in placeholders:
        filepath = os.path.join(static_dir, filename)
        create_placeholder_image(filepath, text)

if __name__ == "__main__":
    main() 