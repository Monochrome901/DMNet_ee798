from tqdm import tqdm
import glob
import os
import argparse
from plot_utils import overlay_image
from density_slide_utils import split_overlay_map, save_cropped_result
from eval_utils import measure_hit_rate

"""
Code for DMnet, density crops generation
Author: Changlin Li
Code revised on : 7/16/2020

Given dataset(train/val/test) generate density crops for given dataset.
Default format for source data: The input images are in jpg format and raw annotations are in txt format 
(Based on Visiondrone 2018/19/20 dataset)

The data should be arranged in following structure before you call any function within this script:
dataset(Train/val/test)
--------images
--------dens (short for density map)
--------Annotations (Optional, but not available only when you conduct inference steps)

Sample running command:
python density_slide_window_official.py . height_width threshold --output_folder output_folder --mode val
"""


def measure_hit_rate_on_data(file_list, window_size, threshold, output_dir, mode="train"):
    """
    Serve as a function to measure how many bboxs we missed for DMNet. It helps estimate the performance of
    bounding boxes
    :param file_list: The annotations file lists to collect
    :param window_size: The kernel to slide. The size comes from EDA result
    :param threshold: Determine if current crop is ROI. We keep crops only when the sum > threshold
    :param output_dir: The output dir to save result
    :param mode: dataset to use
    :return:
    """
    count_data = total_data = 0
    for file in tqdm(file_list, total=len(file_list)):
        overlay_map = overlay_image(file, window_size, threshold, output_dir)
        result = split_overlay_map(overlay_map)
        count, total = measure_hit_rate(file.replace("images", "annotations").replace("jpg", "txt"), result, mode)
        count_data += count
        total_data += total
    print("hit rate is: " + str(round(count_data / total_data * 100.0, 2)))


def parse_args():
    parser = argparse.ArgumentParser(
        description='DMNet--Generate density crops from given density map')
    parser.add_argument('root_dir', default="dataset", help='the path for source data')
    parser.add_argument('window_size', help='The size of kernel, format: h_w')
    parser.add_argument('threshold', type=float, help='Threshold defined to select the cropped region')
    parser.add_argument('--image_prefix', default=".jpg", help='the path to save precomputed distance')
    parser.add_argument('--output_folder', help='The dir to save generated images and annotations')
    parser.add_argument('--mode', default="val", help='Indicate if you are working on train/val/test set')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # Parse arguments
    args = parse_args()
    mode = args.mode
    root_dir = args.root_dir
    folder_name = args.output_folder
    data_root = f'{root_dir}/{mode}'  # Set to dataset/val

    # Collect image and annotation files from dataset/val
    img_array = glob.glob(f'{data_root}/images/*.jpg')
    anno_path = glob.glob(f'{data_root}/annotations/*.txt')

    # Create output directories
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)

    # Window size and threshold
    window_size = args.window_size.split("_")
    window_size = (int(window_size[0]), int(window_size[1]))
    threshold = args.threshold

    # Define output directories
    output_img_dir = os.path.join(folder_name, mode, "images")
    output_anno_dir = os.path.join(folder_name, mode, "annotations")
    
    # Ensure output directories exist
    os.makedirs(output_img_dir, exist_ok=True)
    os.makedirs(output_anno_dir, exist_ok=True)

    # Save cropped results
    save_cropped_result(img_array, window_size, threshold, None, output_img_dir, output_anno_dir, mode=mode)
