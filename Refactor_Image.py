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

junk_folder = [".DS_Store", "images", "js", "styles.css"]
for folder in os.listdir(base):
    folder_path = os.path.join(base, folder)

    if (folder in junk_folder):
        continue

    folder_path += "/Pictures"

    for file in os.listdir(folder_path):
        # Replace "jpeg" with "jpg" in the file name
        new_file_name = file.replace("jpeg", "jpg")

        # Construct the new file path
        new_file_path = folder_path
        new_file_path += "/"
        new_file_path += new_file_name

        # Rename the file
        #os.rename(folder_path, new_file_path)




# If you want to include the full path to the files, you can use os.path.abspath
#file_paths = [os.path.abspath(os.path.join(folder_path, f)) for f in files]
