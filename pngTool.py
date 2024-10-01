from PIL import Image, ImageDraw
import numpy as np

scaleFactor = 5

# key dimensions subject to change
toolLength = 70
toolDiameter = 5

# other dimensions defining the toolhead geometry
xArray = np.array([20, 50, toolLength]) * scaleFactor
dArray = np.array([50, 40, toolDiameter]) * scaleFactor

# draw white image of correct size
width, height = dArray[0], np.sum(xArray)
image = Image.new('RGB', (width, height), 'black')
draw = ImageDraw.Draw(image)

# defining coodinates for shapes
shapeArray = [
    ("rectangle1", (0, 0, width, xArray[0])),
    ("rectangle1", ((width-dArray[1])/2, xArray[0], width-((width-dArray[1])/2), xArray[0]+xArray[1])),
    ("rectangle2", ((width-dArray[2])/2, height-xArray[2], width-((width-dArray[2])/2), height-(dArray[2]/2))),
    ("circle", ((width-dArray[2])/2, height-dArray[2], width-((width-dArray[2])/2), height))
]

# drawing shapes
for shape in shapeArray:
    if shape[0] == "rectangle1":
        draw.rectangle(shape[1], fill = 'white')
    if shape[0] == "rectangle2":
        draw.rectangle(shape[1], fill = 'white')
    if shape[0] == "circle":
        draw.ellipse(shape[1], fill = 'white')

# save an preview the png
image.save('/Users/hamzahchariwala/Desktop/CloudNC_Hackathon/toolhead.png')
# image.show()

