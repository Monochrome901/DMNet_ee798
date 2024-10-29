import os
import subprocess

def run_script(command):
    """Run a shell command."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error running: {command}")
        exit(1)

def main():
    # Set paths and variables
    dataset_folder = "dataset"
    # gaussian_kernels = "gaussian_kernels.pkl"
    # distances_dict = "distances_dict.pkl"
    output_folder = "output"
    mode = "val"
    
    # Step 1: Run annotations_correct.py
    print("Running annotations_correct.py...")
    # run_script("python annotations_correct.py")
    
    # Step 2: Run Generate_density_map_official.py
    print("Running Generate_density_map_official.py...")
    # run_script(f"python Generate_density_map_official.py {dataset_folder} --mode {mode}")
    
    # Step 3: Run model.py
    print("Running model.py...")
    run_script("python model2.py")
    
    # Step 4: Run density_slide_window_official.py
    print("Running density_slide_window_official.py...")
    run_script(f"python density_slide_window_official.py {dataset_folder} 70_70 0.08 --output_folder {output_folder} --mode {mode}")

if __name__ == "__main__":
    main()
