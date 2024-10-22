
---

# DMNet_ee798

This repository implements the paper:  
**[Density Map Guided Object Detection in Aerial Images](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w11/Li_Density_Map_Guided_Object_Detection_in_Aerial_Images_CVPRW_2020_paper.pdf)**  
This project addresses object detection challenges in high-resolution aerial images by using density map-guided image cropping to improve detection accuracy.

## Table of Contents
1. [Installation](#installation)
2. [Dataset Setup](#dataset-setup)
3. [Running the Project](#running-the-project)
    - [Step 1: Image Cropping](#step-1-image-cropping)
    - [Step 2: Object Detection](#step-2-object-detection)
    - [Step 3: Fusion and Analysis](#step-3-fusion-and-analysis)
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

   - **Output**: A new folder containing cropped images and corresponding annotations.

3. To analyze the cropped images, use the script:

   ```bash
   python results.py
   ```

   - This will generate a histogram comparing the size distribution of the image crops.

### Step 2: Object Detection

1. Organize the cropped dataset for object detection:

   ```
   Object_detection_fusion/
   ├── Dataset/
   │   ├── Global/
   │   │   ├── images/
   │   │   └── annotations/
   │   └── Density/
   │       ├── images/
   │       └── annotations/
   ```

2. Run the object detection model using the following script:

   ```bash
   python predictions.py
   ```

   - **Pretrained weights**: You can find the pretrained YOLOv5 weights [here](#) and the training notebook [here](#).

### Step 3: Fusion and Analysis

1. To combine detection results from the cropped images and the original images, run:

   ```bash
   python fusion_detection_result_official.py
   ```

2. To evaluate the model’s performance, run:

   ```bash
   python analysis.py
   ```

   - This will provide scores for various detection metrics.

---

## Pretrained Models

- **MCNN Pretrained Weights**: [Download here](#)
- **YOLOv5 Pretrained Weights**: [Download here](#)
- **Training Notebook**: [Available on Kaggle](#)

---

## References
- https://github.com/Cli98/DMNet/tree/master?tab=readme-ov-file
- https://github.com/CommissarMa/MCNN-pytorch

---
