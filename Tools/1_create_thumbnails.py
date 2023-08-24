#  python3 Tools/resize.py
import cv2
import os


def makeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


makeDir("Thumbnails")
KeyFrames_folder = "Images"
subMainFolders = [f.path for f in os.scandir(KeyFrames_folder) if f.is_dir()]
for fFolder in subMainFolders:
    print("Processing: {}".format(fFolder))
    childFolders = [f.path for f in os.scandir(fFolder) if f.is_dir()]
    for sFolder in childFolders:
        if not os.path.exists(sFolder.replace("Images", "Thumbnails")):
            makeDir(sFolder.replace("Images", "Thumbnails"))
            for image in os.listdir(sFolder):
                img = cv2.imread(os.path.join(sFolder, image), 1)
                img_resized = cv2.resize(img, (0, 0), fx=0.2, fy=0.2)
                cv2.imwrite(os.path.join(sFolder.replace("Images", "Thumbnails"), image), img_resized)
