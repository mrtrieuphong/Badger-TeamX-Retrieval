# python3 Tools/extraction.py
import numpy as np
from pathlib import Path

Features_folder = "Features"
feature_merged = []
features_list = []

for features_file in sorted(Path(Features_folder).glob("*.npy")):
    features_list.append(np.load(features_file))

# Concatenate the features and store in a merged file
features = np.concatenate(features_list)
np.save("features.npy", features)
