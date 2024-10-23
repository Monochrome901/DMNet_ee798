import shutil
from ultralytics import YOLO
from pathlib import Path
import os
from tqdm import tqdm
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run predictions and replace annotations.')
parser.add_argument('val_images_dir', type=str, help='Path to validation images directory')
parser.add_argument('target_dir', type=str, help='Path to target annotations directory')
parser.add_argument('model_weights', type=str, help='Path to model weights file (e.g., best.pt)')

args = parser.parse_args()

# Convert the input paths to Path objects
val_images_dir = Path(args.val_images_dir)
target_dir = Path(args.target_dir)
model_weights = args.model_weights

# Delete the output directory if it exists
output_dir = Path('output')
if output_dir.exists():
    shutil.rmtree(output_dir)

# Recreate the output directory for annotations
output_dir.mkdir(exist_ok=True)

# Load the trained model from the specified weights file
model = YOLO(model_weights)

# Run predictions on the validation set using the trained model
results = model.predict(source=str(val_images_dir), save_txt=True, save_conf=True)

# Class list (if needed for future reference)
classList = ["pedestrian", "people", "bicycle", "car", "van", "truck", "tricycle", "awning-tricycle", "bus", "motor"]

# Convert the results to the desired annotation format and save them
for result in tqdm(results):
    # Get the corresponding image file name and create the annotation file name
    img_name = Path(result.path).stem
    ann_file = output_dir / f"{img_name}.txt"
    
    # Write annotations in the required format
    with open(ann_file, 'w') as f:
        for box in result.boxes:
            cls_id = int(box.cls)  # Get class ID
            bbox = box.xyxy[0].tolist()  # Get bounding box in absolute pixel format (xyxy)
            
            # Create the line with class and bounding box values formatted for the annotation file
            line = f"{cls_id} {' '.join(f'{coord:.6f}' for coord in bbox)}\n"
            f.write(line)

print(f"Predictions saved as annotations in {output_dir}")

# Replace the annotations in the target directory with those in output directory
for ann_file in output_dir.iterdir():
    if ann_file.is_file():
        # Define the corresponding file in the target directory
        target_file = target_dir / ann_file.name
        
        # Copy the annotation file to the target directory (overwrite if exists)
        shutil.copyfile(ann_file, target_file)

print(f"Annotations in {target_dir} have been replaced with new predictions.")
