# create the 32x32 file icon of the project.

# This script requires the Python Imaging Library (PIL) to be installed.
# If you don't have PIL, you can install it with pip:
# pip install pillow

from PIL import Image, ImageDraw, ImageFont

if __name__ == '__main__':
    # Define the icon size and colors
    icon_size = (32, 32)
    background_color = (0, 119, 199)  # Sky blue
    text_color = (226, 244, 254) # gray
    green = (0, 255, 0)  # Green
    red = (255, 0, 0)  # Red

    # Create a new image with the background color
    icon = Image.new('RGB', icon_size, background_color)
    # Create a drawing context
    draw = ImageDraw.Draw(icon)
    # Load a font file
    font = ImageFont.truetype('arial.ttf', 20)
    # Draw text
    draw.rectangle((0, 0, 16, 16), fill=red)
    draw.text((2, 5), 'PM', fill=text_color, font=font)
    # Save the icon file
    icon.save('jh-pdf-merger.ico', 'ICO')
