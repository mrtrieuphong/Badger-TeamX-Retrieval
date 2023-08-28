# python3 Tools/2_create_photo_ids.py
import os

data_list = []

Thumbnails_folder = "Thumbnails"
subMainFolders = [f.path for f in os.scandir(Thumbnails_folder) if f.is_dir()]
for fFolder in subMainFolders:
    childFolders = [f.path for f in os.scandir(fFolder) if f.is_dir()]
    for sFolder in childFolders:
        for image in os.listdir(sFolder):
            data_list.append(os.path.join(sFolder.strip(".."), image))
data_list.sort()
with open("photo_ids.csv", "w", encoding="utf-8") as w:
    w.write("photo_id\n")
    for photo_id in data_list:
        w.write(photo_id.replace("\\", "/") + '\n')