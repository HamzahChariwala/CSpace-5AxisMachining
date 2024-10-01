import Tools
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.ndimage import zoom


resolution = 1
tool_height, tool_diameter, stock_height = [200 * resolution, 5 * resolution, 100 * resolution]

initial_tool_array, initial_tool_array_size = Tools.convert_and_scale_png('toolhead.png', tool_height)
initial_part_array, initial_part_array_size = Tools.convert_and_scale_png('partProfile.png', tool_height)

grid_size = Tools.calculate_necessary_grid_size(50, initial_tool_array_size, initial_part_array_size)

top_padding, side_padding = Tools.calculate_padding_required(grid_size, initial_part_array_size)
stock_only_array = Tools.replace_values_in_array(initial_part_array, [0, 1])
padded_part = Tools.padding(initial_part_array, top_padding, 0, side_padding)
padded_stock = Tools.padding(stock_only_array, top_padding, 0, side_padding)

finishing_outline = Tools.create_outline(tool_diameter, padded_part, [1,2])
roughing_initial_outline = Tools.create_outline(tool_diameter, padded_stock, [1,2])
truncated_tool_array = Tools.truncate_tool(initial_tool_array, int(tool_diameter/2), tool_diameter)

# test = Tools.place_object_on_image(truncated_tool_array, finishing_outline+padded_part, [200, 250])

# plt.imshow(test, cmap='gray')
# plt.show()

# rotated_tool = Tools.rotate_image_anticlockwise(truncated_tool_array, 60)


# feasible_points, feasible_indices, grids = Tools.test_for_given_orientation(rotated_tool, padded_part, finishing_outline)



# fig = plt.figure(figsize=(10, 3))
# ax1, ax2 = fig.subplots(1, 1)
# plt.imshow(grids[5], cmap='gray')
# plt.show()

# test = Tools.rotate_image_anticlockwise(truncated_tool_array, -90)
# plt.imshow(test, cmap='gray')
# plt.show()

angles = [-48, -3, 20]

# for i in range(-160, 161, 1):
#     angles.append(i)
    
indices, grids, fractions, checkpoints = Tools.full_run(truncated_tool_array, padded_part, finishing_outline, angles)
print(fractions)

final_grid = Tools.present_CSpace(checkpoints, indices, angles)
fig = plt.figure(figsize=(10,3))
ax1= fig.subplots(1,1)
ax1.imshow(final_grid, cmap="gray")

# fig = plt.figure(figsize=(10,3))
# ax1, ax2, ax3, ax4= fig.subplots(1,4)
# ax1.imshow(grids[3][48]+finishing_outline, cmap="gray")
# ax2.imshow(grids[1][266]+finishing_outline, cmap="gray")
# ax3.imshow(grids[5][348]+finishing_outline, cmap="gray")
# ax4.imshow(grids[2][156]+finishing_outline, cmap="gray")

plt.show()

