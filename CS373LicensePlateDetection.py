import math
import sys
from pathlib import Path

from matplotlib import pyplot
from matplotlib.patches import Rectangle

# import our basic, light-weight png reader library
import imageIO.png

# this function reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
def readRGBImageToSeparatePixelArrays(input_filename):

    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))

    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)


# a useful shortcut method to create a list of lists based array representation for an image, initialized with a value
def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):

    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array

def computeRGBToGreyscale(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
    
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    for i in range (image_height):
        for j in range(image_width):
            greyscale_pixel_array[i][j] = round(0.299*pixel_array_r[i][j] + 0.587*pixel_array_g[i][j] + 0.114*pixel_array_b[i][j])
    
    return greyscale_pixel_array
def computeStandardDeviationImage5x5(pixel_array, image_width, image_height):
    out_pixel = [[0 for i in range(image_width)][:] for j in range(image_height)]
    for row in range(2, image_height - 2):
        for col in range(2, image_width - 2):
            out_pixel[row][col] = standard([
                pixel_array[row- 2][col- 2],
                pixel_array[row - 2][col],
                pixel_array[row - 2][col + 2],
                pixel_array[row + 2][col - 2],
                pixel_array[row + 2][col],
                pixel_array[row + 2][col + 2],
                pixel_array[row][col - 2],
                pixel_array[row][col],
                pixel_array[row][col + 2]
            ])
    return out_pixel

def standard(new_list):
    value = sum(new_list) / len(new_list)
    var = 0
    for i in new_list:
        result = i - value
        var += result ** 2
    return (var / len(new_list)) ** 0.5
def computeMinAndMaxValues(pixel_array, image_width, image_height):
    min1 = pixel_array[0][0]
    max1 = pixel_array[0][0]
    for row in pixel_array:
        for value in row:
            if value < min1:
                min1 = value
            if value > max1:
                max1 = value
    return (min1, max1)
def computeThresholdGE(pixel_array, thresholded,image_width, image_height):
    thresholded = list()
    for i in range(image_height):
        index = list()
        for j in range(image_width):
            if(pixel_array[i][j] < 150):
                index.append(0)
            else:
                index.append(255)
        thresholded.append(index)
    return thresholded
    
def printPixelArray(thresholded):
    for row in thresholded:
        print(*row)


def scaleTo0And255AndQuantize(pixel_array, image_width, image_height):
    result = createInitializedGreyscalePixelArray(image_width, image_height)

    minmax = computeMinAndMaxValues(pixel_array, image_width, image_height)

    if minmax[0] == minmax[1]:
        return result

    for i in range(len(pixel_array)):
        for j in range(len(pixel_array[0])):
            result[i][j] = round((pixel_array[i][j] - minmax[0]) / (minmax[1] - minmax[0]) * 255)
    return result
def computeErosion8Nbh3x3FlatSE(pixel_array, image_width, image_height):
    list= createInitializedGreyscalePixelArray(image_width, image_height)
    for i in range(image_height):
        for j in range(image_width):
            new_list=[]
            for x in range(i-1, i+2):
                for y in range(j-1, j+2):
                    if x < 0 or y < 0 or x >= image_height or y >= image_width:
                        new_list.append(0)
                    else:
                        new_list.append(pixel_array[x][y])
            if min(new_list) >0:
                list[i][j] = 1
    return list
def computeDilation8Nbh3x3FlatSE(pixel_array, image_width, image_height):
    list= createInitializedGreyscalePixelArray(image_width, image_height)
    for i in range(image_height):
        for j in range(image_width):
            new_list=[]
            for x in range(i-1, i+2):
                for y in range(j-1, j+2):
                    if x < 0 or y < 0 or x >= image_height or y >= image_width:
                        new_list.append(0)
                    else:
                        new_list.append(pixel_array[x][y])
            if max(new_list) >0:
                list[i][j] = 1
    return list
class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def computeConnectedComponentLabeling(pixel_array, image_width, image_height):
    result = [[0 for i in range(image_width)] for i in range(image_height)]
    label = 0
    dic = {}
    for i in range(image_height):
        for x in range(image_width):
            if pixel_array[i][x] != 0 and result[i][x]  == 0:
                queue = Queue()
                label += 1
                dic[label] = 1
                result[i][x] = 1
                queue.enqueue((i, x))
                while queue.size() != 0:
                    index = queue.dequeue()
                    pixel_array[index[0]][index[1]] = label

                    if index[1] != image_width-1:
                        if pixel_array[index[0]][index[1] + 1] != 0 and result[index[0]][index[1] + 1] == 0:
                            queue.enqueue((index[0], index[1] + 1))
                            result[index[0]][index[1] + 1] = 1
                            dic[label] += 1
                    if index[0] != image_height-1:
                        if pixel_array[index[0] + 1][index[1]] != 0 and result[index[0] + 1][index[1]] == 0:
                            queue.enqueue((index[0] + 1, index[1]))
                            result[index[0] + 1][index[1]] = 1
                            dic[label] += 1
                    if index[0] != 0:
                        if pixel_array[index[0] - 1][index[1]] != 0 and result[index[0] - 1][index[1]] == 0 :
                            queue.enqueue((index[0] - 1, index[1]))
                            result[index[0] - 1][index[1]] = 1
                            dic[label] += 1
                    if index[1] != 0:
                        if pixel_array[index[0]][index[1] - 1] != 0 and result[index[0]][index[1] - 1] == 0:
                            queue.enqueue((index[0], index[1] - 1))
                            result[index[0]][index[1] - 1] = 1
                            dic[label] += 1

    return (pixel_array, dic)
# This is our code skeleton that performs the license plate detection.
# Feel free to try it on your own images of cars, but keep in mind that with our algorithm developed in this lecture,
# we won't detect arbitrary or difficult to detect license plates!
def main():

    command_line_arguments = sys.argv[1:]

    SHOW_DEBUG_FIGURES = True

    # this is the default input image filename
    input_filename = "numberplate1.png"

    if command_line_arguments != []:
        input_filename = command_line_arguments[0]
        SHOW_DEBUG_FIGURES = False

    output_path = Path("output_images")
    if not output_path.exists():
        # create output directory
        output_path.mkdir(parents=True, exist_ok=True)

    output_filename = output_path / Path(input_filename.replace(".png", "_output.png"))
    if len(command_line_arguments) == 2:
        output_filename = Path(command_line_arguments[1])


    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(input_filename)

    # setup the plots for intermediate results in a figure
    fig1, axs1 = pyplot.subplots(2, 2)
    axs1[0, 0].set_title('Input red channel of image')
    axs1[0, 0].imshow(px_array_r, cmap='gray')
    axs1[0, 1].set_title('Input green channel of image')
    axs1[0, 1].imshow(px_array_g, cmap='gray')
    axs1[1, 0].set_title('Input blue channel of image')
    axs1[1, 0].imshow(px_array_b, cmap='gray')


    # STUDENT IMPLEMENTATION here
    px_array = computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    px_array = computeStandardDeviationImage5x5(px_array, image_width, image_height)
    px_array = scaleTo0And255AndQuantize(px_array, image_width, image_height)
    px_array = computeThresholdGE(px_array, 150, image_width, image_height)
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height)
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height)
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height)
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height)

    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height)
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height)
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height)
    px_array, d = computeConnectedComponentLabeling(px_array, image_width, image_height)

    for index in d.keys():
        list_x=[]
        list_y=[]
        if (d[index]> 0):
            for i in range(image_height):
                for j in range(image_width):
                    if px_array[i][j]==index:
                        list_x.append(j)
                        list_y.append(i)
            dict_min = list_x[0] ** 2 + list_y[0] ** 2
            dict_max = list_x[0] ** 2 + list_y[0] ** 2
            min = 0
            max = 0
            for k in range(len(list_x)):
                if dict_max < list_x[k] ** 2 + list_y[k] ** 2 and list_x[k] ** 2 + list_y[k] ** 2 <(image_width**2 + image_height**2):
                    dict_max = list_x[k] ** 2 + list_y[k] ** 2
                    max = k
                if dict_min>list_x[k]**2 + list_y[k]**2 and list_x[k]**2 + list_y[k]**2 > 0:
                    dict_min=list_x[k]**2 + list_y[k]**2
                    min = k

            box_min_x = list_x[min]
            box_min_y = list_y[min]

            box_max_x = list_x[max]
            box_max_y = list_y[max]

            box_width = box_max_x - box_min_x
            box_height = box_max_y - box_min_y

            if box_width > 0 and box_height>0:
                if box_width/box_height > 1.5 and box_width/box_height < 6.0:
                    bbox_min_x = box_min_x
                    bbox_max_x = box_max_x
                    bbox_min_y = box_min_y
                    bbox_max_y = box_max_y
    px_array = computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    axs1[1, 1].set_title('Final image of detection')
    axs1[1, 1].imshow(px_array, cmap='gray')
    rect = Rectangle((bbox_min_x, bbox_min_y), bbox_max_x - bbox_min_x, bbox_max_y - bbox_min_y, linewidth=1,
                     edgecolor='g', facecolor='none')
    axs1[1, 1].add_patch(rect)


    # write the output image into output_filename, using the matplotlib savefig method
    extent = axs1[1, 1].get_window_extent().transformed(fig1.dpi_scale_trans.inverted())
    pyplot.savefig(output_filename, bbox_inches=extent, dpi=600)

    if SHOW_DEBUG_FIGURES:
        # plot the current figure
        pyplot.show()


if __name__ == "__main__":
    main()