from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.ndimage import zoom


def convert_and_scale_png(filename, desired_height, added_factor=0):
    path = '/Users/hamzahchariwala/Desktop/CloudNC_Hackathon/' + filename
    png = Image.open(path).convert('L')
    array = np.array(png)/255+added_factor
    height, width = array.shape
    scale_factor = desired_height/height
    resized = zoom(array, scale_factor, order=0)
    size = resized.shape
    return resized, size

def calculate_necessary_grid_size(buffer, tool_size, stock_size):
    height = buffer + tool_size[0] + stock_size[0]
    width = buffer*2 + tool_size[0]*2 + stock_size[1]
    return [height, width]

def calculate_padding_required(target_size, object_size):
    top = round(target_size[0]-object_size[0])
    side = round((target_size[1]-object_size[1])/2)
    return [top, side]

def replace_values_in_array(array, replace_array):
    duplicate = np.copy(array)
    duplicate[duplicate == replace_array[0]] = replace_array[1]
    return duplicate

def padding(array, top, bottom, sides):
    original_size = array.shape
    empty = np.zeros((original_size[0]+top+bottom, original_size[1]+2*sides))
    sideArray = np.zeros((1, sides))
    for index, row in enumerate(array):
        empty[index+top] = np.concatenate((sideArray, row, sideArray), axis=None)
    return empty

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

def part_dilation(array, inflation_mask, replace_array=[0,0]):
    duplicate = np.copy(array)
    if replace_array[0] != replace_array[1]:
        replace_values_in_array(array, replace_array)
    dilated_array = ndimage.binary_dilation(duplicate, structure=inflation_mask)
    return np.array(dilated_array, dtype=int)

def create_outline(circle_mask_size, input_array, replace = [0,0]):
    small = create_circular_mask(circle_mask_size-1)
    normal = create_circular_mask(circle_mask_size+1)
    undersized = part_dilation(input_array, small)
    regular = part_dilation(input_array, normal)
    path = regular - undersized
    final = replace_values_in_array(path, replace)
    return final

def truncate_tool(input_array, remove_num, tool_diameter):
    height, width = input_array.shape
    start = height-remove_num
    duplicate = np.copy(input_array)
    for i in range(remove_num):
        duplicate = np.delete(duplicate, start, 0)
    new_size = duplicate.shape
    if tool_diameter - (2*remove_num) != 0:
        duplicate[new_size[0]-1][int(new_size[1]/2)] = 3
    else:
        duplicate[new_size[0]-1][int(new_size[1]/2)] = 3
        duplicate[new_size[0]-1][int(new_size[1]/2)+1] = 3
    return duplicate

def advanced_padding_requirements(image_size, target_size, origin, insert_coordinate):
    target_top, target_bottom = insert_coordinate[0]+1, target_size[0]-(insert_coordinate[0]+1)
    target_left, target_right = insert_coordinate[1]+1, target_size[1]-(insert_coordinate[1]+1)
    image_top, image_bottom = origin[0]+1, image_size[0]-(origin[0]+1)
    image_left, image_right = origin[1]+1, image_size[1]-(origin[1]+1)
    total_top, total_bottom = target_top-image_top, target_bottom-image_bottom
    total_left, total_right = target_left-image_left, target_right-image_right
    return [total_top, total_right, total_bottom, total_left]

def implement_advanced_padding(array, padding):
    top, right, bottom, left = padding
    original_size = array.shape
    empty = np.zeros((original_size[0]+top+bottom, original_size[1]+right+left))
    left_addition = np.zeros((1, left))
    right_addition = np.zeros((1, right))
    for index, row in enumerate(array):
         new_index = index + top
         if new_index < empty.shape[0]:
            empty[new_index] = np.concatenate((left_addition, row, right_addition), axis=None)
    return empty

def find_origin(object, key):
    for index1, row in enumerate(object):
        for index2, value in enumerate(row):
            if value == key:
                return [index1, index2]
            
def find_key_points(image, key):
    checkpoints = []
    for index1, row in enumerate(image):
        for index2, value in enumerate(row):
            if value == key:
                coordinates = [index1, index2]
                checkpoints.append(coordinates)
    return checkpoints

def place_object_on_image(object, image, insert_coordinate):
    origin = find_origin(object, 3)
    padding = advanced_padding_requirements(object.shape, image.shape, origin, insert_coordinate)
    padded_array = implement_advanced_padding(object, padding)
    return padded_array+image

def interference_test(image):
    for index1, row in enumerate(image):
        for index2, value in enumerate(row):
            if value > 1 and value < 3:
                return True
    return False

def rotate_image_anticlockwise(image, angle):
    angle_rad = np.deg2rad(angle)
    # sin_theta, cos_theta = np.sin(angle_rad), np.cos(angle_rad)
    # rotation_matrix = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
    height, width = image.shape
    safety_pad = 10
    target_size = [height + safety_pad, height + safety_pad]
    side_padding = int((target_size[0] - width)/2)
    # origin = [int(height/2), int(width/2)]
    # insert_coordinate = [int(target_size[1]/2), int(target_size[1]/2)]
    # padding_needed = advanced_padding_requirements(image, target_size, origin, insert_coordinate)
    padding_needed = [safety_pad, side_padding, safety_pad, side_padding]
    padded_tool = implement_advanced_padding(image, padding_needed)
    rotated_tool = ndimage.rotate(padded_tool, angle, reshape=False)
    restored_tool = restore_original_values(rotated_tool, "tool")
    # rotated_image = ndimage.rotate(image, angle, reshape=False)
    # rotated_outline = ndimage.rotate(outline, angle, reshape=False)
    # restored_image = restore_original_values(rotated_image, "image")
    # restored_outline = restore_original_values(rotated_outline, "outline")
    return restored_tool

def restore_original_values(array, type):
    new = np.zeros(array.shape)
    # if type == "image": new_value = 1
    # if type == "outline": new_value = 2
    for index1, row in enumerate(array):
        for index2, value in enumerate(row):
            # if type == "image" and value > 0.5: 
            #     new[index1][index2] = 1
            # elif type == "outline" and value > 1.4: 
            #     new[index1][index2] = 2
            if type == "tool" and value > 1.7:
               new[index1][index2] = 3
            elif type == "tool" and value > 0.2:
                new[index1][index2] = 1
            else: new[index1][index2] = 0
    return new

def test_for_given_orientation(object, image, checkpoints):
    grid_set = []
    feasible_points = []
    feasible_points_index = []
    origin = find_origin(object, 3)
    # checkpoints = find_key_points(outline, 2)
    for index, coordinate in enumerate(checkpoints):
        combined_image = place_object_on_image(object, image, coordinate)
        # print(index)
        if interference_test(combined_image) == False:
            # feasible_points.append(coordinate)
            feasible_points_index.append(index)
        grid_set.append(combined_image)
    return feasible_points_index, grid_set

def full_run(object, image, outline, angle_array):
    checkpoints = find_key_points(outline, 2)
    truncated_tool = np.copy(object)
    indices, grids, fractions = [], [], []
    for angle in angle_array:
        rotated_tool = rotate_image_anticlockwise(truncated_tool, angle)
        print(f"tool rotated to {angle} degrees")
        index_list, grid_array = test_for_given_orientation(rotated_tool, image, checkpoints)
        proportion = len(index_list)/len(checkpoints)
        print(f"tool successfully tested at {angle} degrees")
        indices.append(index_list)
        grids.append(grid_array)
        fractions.append(proportion)
    return indices, grids, fractions, checkpoints

def identify_missed_checkpoints(data_grid):
    transpose = np.transpose(data_grid)
    for index, row in enumerate(transpose):
        total_sum = np.sum(row)
        if total_sum == 0:
            for index2, value in enumerate(row):
                transpose[index][index2] = -1
    corrected_grid = np.transpose(transpose)
    return corrected_grid

def present_CSpace(checkpoints, indices, angles):
    empty = np.zeros((len(angles), len(checkpoints)))
    for num, angle in enumerate(angles):
        for index in indices[num]:
            empty[num][index] = 1
    missed_points = identify_missed_checkpoints(empty)
    return missed_points

