
---

# DMNet_ee798

This repository implements the paper:  
**[Density Map Guided Object Detection in Aerial Images](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w11/Li_Density_Map_Guided_Object_Detection_in_Aerial_Images_CVPRW_2020_paper.pdf)**  
This project addresses object detection challenges in high-resolution aerial images by using density map-guided image cropping to improve detection accuracy.

## Table of Contents
1. [Installation](#installation)
2. [Dataset Setup](#dataset-setup)
3. [Running the Project](#running-the-project)
    - [Image Cropping](#step-1-image-cropping)
    - [Object Detection](#step-3-object-detection)
    - [Fusion and Analysis](#step-4-fusion-and-analysis)
    - [Results/Analysis](#step-5-analysis/results)
4. [Pretrained Models](#pretrained-models)
5. [References](#references)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/DMNet_ee798.git
   cd DMNet_ee798
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

---

## Dataset Setup

Download the VisionDrone dataset from **[this link](#)** and organize it as follows:

```
Image_cropping/
├── Dataset/
│   ├── val/
│   ├── test/
│   └── train/
│       ├── images/
│       └── annotations/
```

Place the images and annotations into their respective folders (`images/` and `annotations/`).

---

## Running the Project

### Step 1: Image Cropping

1. Navigate to the `Image_cropping` directory:

   ```bash
   cd Image_cropping
   ```

2. Run the cropping script:

   ```bash
   python run_all.py
   ```

   - **Output**: A new folder containing cropped images and corresponding annotations. (Most of the code in this part is taken from the given references)
   - **What actually happened?** -
    1. Make the annotations file as per the model requirements (removing last two columns)
    2. Creating ground truth density maps with Generate_density_map_official.py (in .npy format)
    3. Predicting density maps using model.py (in .npy format)
    4. Creating cropped images with desnity_slide_window_official.py (stores them in output folder)

3. To analyze the cropped images, use the script:

   ```bash
   python results.py
   ```

   - This will generate a histogram comparing the size distribution of the image crops.
### Dataset Setup

Organize the cropped dataset and the original dataset inside the fusion_detection folder:

```
fusion_detection/
├── Dataset/
│   ├── Global/
|   |   |- val  
│   │   |   |── images/
│   │   |   |── ground_annotations/
│   └── Density/
│   |   |- val  
│   │   |   |── images/
│   │   |   |── ground_annotations/
```
## As I could not get the mmdetection to run, Almost all code from this point onwards has been implemented from scratch
### Step 2: Annotations correction
```bash
clean_annotation.py
```
This will make some minor changes in the annotations of the cropped images.

### Step 3: Object Detection
```bash
python model.py .\dataset\Global\val\images\ .\dataset\Global\val\ .\best.pt
python model.py .\dataset\Density\val\images\ .\dataset\Density\val\ .\best.pt
```
This will create the folder annotations inside Density and Global with predicted annotations

### Step 4: Fusion and Analysis
```bash
python .\fusion_detection_result_official.py --root_dir dataset --mode val
```
Combines detection results from the cropped images and the original images
To evaluate the model’s performance, run:
### Step 5: Analysis/Results
```bash
python analysis.py
```
This will provide sample outputs and store them in the output folder
```bash
python analysis2.py
```
returns the mAP scroe

---

## Pretrained Models

- **MCNN Pretrained Weights**: [Download here](https://drive.google.com/file/d/1J--qH8_djZIsX3YUz9IkysWsfxzKXEqI/view?usp=sharing)
- **YOLOv5 Pretrained Weights**: [Download here](https://drive.google.com/file/d/1VEYrmYIZTTnpmPiRvY-Zbz_jTzKr0lh1/view?usp=sharing)
- **Training Notebook**: [Available on Kaggle](https://www.kaggle.com/code/monochrome902/visdrone-training)

---

## References
- https://github.com/Cli98/DMNet/tree/master?tab=readme-ov-file
- https://github.com/CommissarMa/MCNN-pytorch

---
