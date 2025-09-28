from PIL import Image
import random

# Set image size
width = 200
height = 200

# Create new image with random color
img = Image.new('RGB', (width, height), 
    (random.randint(0,255), random.randint(0,255), random.randint(0,255)))

# Save the image
img.save('random_color.png')
print("Random image created: random_color.png")