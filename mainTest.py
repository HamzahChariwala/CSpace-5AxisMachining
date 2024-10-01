from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.ndimage import zoom


resolution_multiplier = 1
desired_tool_height = 200*resolution_multiplier
desired_stock_height = 100*resolution_multiplier
selected_tool_diameter = 10*resolution_multiplier

# IMPORT TOOL DIMENSIONS

toolhead_path = '/Users/hamzahchariwala/Desktop/CloudNC_Hackathon/toolhead.png'
toolhead_png = Image.open(toolhead_path).convert('L')
toolhead_convert = np.array(toolhead_png)/255+4
toolhead_length, toolhead_width = toolhead_convert.shape

tool_scale_factor = desired_tool_height/toolhead_length
resized_tool = zoom(toolhead_convert, tool_scale_factor, order=0)
final_tool_shape = resized_tool.shape

# IMPORT PART/STOCK DIMENSIONS

stock_path = '/Users/hamzahchariwala/Desktop/CloudNC_Hackathon/partProfile.png'
stock_png = Image.open(stock_path).convert('L')
stock_convert = np.array(stock_png)/255+1
stock_height, stock_width =  stock_convert.shape

stock_scale_factor = desired_stock_height/stock_height
resized_stock = zoom(stock_convert, stock_scale_factor, order=0)
final_stock_shape = resized_stock.shape

# CREATE MAIN GRID

safety_buffer = 10
grid = np.zeros((safety_buffer+final_stock_shape[0]+final_tool_shape[0],
                 final_tool_shape[0]*2+final_stock_shape[1]+2*safety_buffer))
grid_size = grid.shape

def padding(array, top, bottom, sides):
    original_size = array.shape
    empty = np.zeros((original_size[0]+top+bottom, original_size[1]+2*sides))
    sideArray = np.zeros((1, sides))
    for index, row in enumerate(array):
        empty[index+top] = np.concatenate((sideArray, row, sideArray), axis=None)
    return empty

top_padding_needed = round((grid_size[0]-final_stock_shape[0]))
side_padding_needed = round((grid_size[1]-final_stock_shape[1])/2)
padded_stock = padding(resized_stock, top_padding_needed, 0, side_padding_needed)
# part_only = padded_stock
# stock_only = padded_stock
# test = grid + padded_stock

# part_only[part_only == 1] = 0
# stock_only[stock_only == 2] = 1
# test = ndimage.binary_dilation(part_only, structure=resized_tool)
# test = ndimage.binary_dilation(stock_only, structure=resized_tool)

def create_circular_mask(scaled_size):
    centre = scaled_size/2
    zeros = np.zeros((scaled_size, scaled_size))

    for row in range(scaled_size):
        for column in range(scaled_size):
            y_pad = 1* row < centre
            x_pad = 1* column < centre
            y = row-centre+y_pad
            x = column-centre+x_pad
            radius = np.sqrt(x**2+y**2)

            if radius <= centre:
                zeros[row][column] = 1

    return zeros

def part_dilation(array, inflation_mask):
    duplicate = np.copy(array)
    duplicate[duplicate == 1] = 0
    dilated_array = ndimage.binary_dilation(duplicate, structure=inflation_mask)
    return np.array(dilated_array, dtype=int)

def stock_dilation(array, inflation_mask):
    duplicate = np.copy(array)
    duplicate[duplicate == 2] = 1
    dilated_array = ndimage.binary_dilation(duplicate, structure=inflation_mask)
    return np.array(dilated_array, dtype=int)

circular_mask = create_circular_mask(selected_tool_diameter)

part_test = part_dilation(padded_stock, resized_tool)
stock_test = stock_dilation(padded_stock, resized_tool)

# # print(grid.shape)

sumArray = part_test + stock_test

plt.imshow(padded_stock, cmap='gray')
plt.show()

print(grid_size)
print(final_tool_shape[0])

