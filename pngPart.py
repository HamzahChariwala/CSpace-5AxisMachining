# SCRIPT NOT CURRENTLY WORKING
# KEY DEPENDICIES MISSING - IGNORE FOR NOW

# import cairosvg
from PIL import Image
import numpy as np
import io

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

svgPath = '/Users/hamzahchariwala/Desktop/CloudNC_Hackathon/partProfile.svg'
# pngData = cairosvg.svg2png(url=svgPath)
# image = Image.open(io.BytesIO(pngData).convert('L'))

drawing = svg2rlg(svgPath)
image_data = io.BytesIO()
renderPM.drawToFile(drawing, image_data, fmt='PNG')
image_data.seek(0)
image = Image.open(image_data)

print(image)