from PIL import Image, ImageOps, ImageFilter
import os

#https://stackoverflow.com/questions/67298357/how-to-resize-images-without-keeping-the-aspect-ratio

base = "C:/Users/aprui/OneDrive/Documents/UAB School/UAB_Year_4_Sem_1/CS 499/CS499-FinalProject/static/"
group = "Seafood"
end = "/Pictures"
folder_path = base + group + end

files = []
# Get a list of all files in the folder
for file in os.listdir(folder_path):
    if (os.path.isfile(os.path.join(folder_path, file))):
        files.append(file)

# If you want to include the full path to the files, you can use os.path.abspath
file_paths = [os.path.abspath(os.path.join(folder_path, f)) for f in files]


# # Print the list of file names
# for file in files:
#     print(file)

# # Or print the list of file paths
# for file_path in file_paths:
#     print(file_path)

# listofimages = ['one.jpg', 'two.jpg', 'three.jpg','four.jpg', 'five.jpg', 'six.jpg']

# def get_avg_size(listofimages):
#     h, w = 0, 0
#     for p in listofimages:
#         im = Image.open(p)
#         width, height = im.size
#         h += height
#         w += width
#         print('Process image {0} and height-weight is {1} '.format(p, im.size))

#     print('Calculate average w-h: {0} ~ {1}'.format(w //len(listofimages), h//len(listofimages)))
#     return w//len(listofimages), h//len(listofimages)


def _convert_in_same_size(width, height, files):
    sizes = width, height
    for p in files:
        images = Image.open(p)
        images.thumbnail(sizes)
        images.save(p)
        print(f'Saved image {p} and size is {sizes}')


# get_width, get_height = get_avg_size(listofimages)

height = 1400
width = 1400
_convert_in_same_size(height, width, file_paths)