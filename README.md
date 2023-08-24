# Badger TeamX Video Retrieval
### Developed from the AI Challenge 2022
Video retrieval interface based on AI.

![](screenshot.png)

## Features
- [x] Retrieve images based on english description, similar images, keywords, hybrids,...
- [x] Context slider supports viewing frames around keyframes
- [x] Select and load local or full data partition
- [x] Access online youtube videos at any time or frame
- [x] Queue, add new or delete selected frame at any position
- [x] Export the queue as a file (*.csv) for the qualifying round
- [x] Load, edit and submit final results via API
- [x] Adjust output quantity, show real-time search results
- [x] Manage search results based on multi-tabs
   

## Installation and Running
- Requires at least 120GB of available storage
- Now available on Windows, MacOS and Linux
- Requirements: Python >= 3.8, <= 3.10.
- Recommended: [Miniconda/Anaconda](https://docs.conda.io/en/latest/miniconda.html).

### Download source code
2. Install [git](https://git-scm.com/download/win).
3. Download the `badger-teamx-retrieval` repository
```bash
git clone https://github.com/mrtrieuphong/badger-teamx-retrieval.git
cd badger-teamx-retrieval
```

### Create environment
1. Use `Conda` **[Recommended]**
```bash
conda create -n badger python=3.8
conda activate badger-venv
```
2. Use `virtualenv`
```bash
pip install virtualenv
python3 -m venv badger-venv
# MacOS, Ubuntu
source badger-venv/bin/activate
# Windows
badger-venv/Scripts/activate
```

### Install requirements
```bash
pip install -r requirements.txt
```

### Download required
1. [OpenAI CLIP model](https://github.com/openai/CLIP/blob/main/clip/bpe_simple_vocab_16e6.txt.gz): ../CLIP/clip/bpe_simple_vocab_16e6.txt.gz
2. Images dataset: ../Images
3. Features: ../Features

### Prepare Materials
1. Create thumbnails
```bash
python3 Tools/1_create_thumbnails.py
```
2. Create photo ids
```bash
python3 Tools/2_create_photo_ids.py
```
3. Create features
```bash
python3 Tools/3_create_features.py
```
4. Create mapping
```bash
python3 Tools/4_create_mapping.py
```