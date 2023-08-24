import torch
import numpy as np
import pandas as pd
from CLIP.clip import clip
from PyQt5.QtCore import QSize

ICON_SIZE = 130
ITEM_SIZE = QSize(130, 130)
ICON_PATH = 'UI/statics/logo.png'
token = "YOUR_TOKEN_HERE"


def c00():
    photo_features_c00 = np.load("CLIP/L01/features.npy")
    photo_ids_c00 = pd.read_csv("CLIP/L01/photo_ids.csv", dtype=str)
    photo_ids_c00 = list(photo_ids_c00['photo_id'])
    return photo_features_c00, photo_ids_c00


def c01():
    photo_features_c01 = np.load("CLIP/C01_V0X/features.npy")
    photo_ids_c01 = pd.read_csv("CLIP/C01_V0X/photo_ids.csv", dtype=str)
    photo_ids_c01 = list(photo_ids_c01['photo_id'])
    return photo_features_c01, photo_ids_c01


def c02():
    photo_features_c02 = np.load("CLIP/C02_V0X/features.npy")
    photo_ids_c02 = pd.read_csv("CLIP/C02_V0X/photo_ids.csv", dtype=str)
    photo_ids_c02 = list(photo_ids_c02['photo_id'])
    return photo_features_c02, photo_ids_c02


def cTotal():
    photo_features_all = np.load("CLIP/TOTAL/features.npy")
    photo_ids_all = pd.read_csv("CLIP/TOTAL/photo_ids.csv", dtype=str)
    photo_ids_all = list(photo_ids_all['photo_id'])
    return photo_features_all, photo_ids_all


# Load the open CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/16", device=device)
