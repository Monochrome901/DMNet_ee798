from torch.utils.data import Dataset
import os
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import cv2
import torch.nn.functional as F
import matplotlib.cm as CM

class CrowdDataset(Dataset):
    '''
    crowdDataset
    '''
    def __init__(self,img_root,gt_dmap_root,gt_downsample=1):
        '''
        img_root: the root path of img.
        gt_dmap_root: the root path of ground-truth density-map.
        gt_downsample: default is 0, denote that the output of deep-model is the same size as input image.
        '''
        self.img_root=img_root
        self.gt_dmap_root=gt_dmap_root
        self.gt_downsample=gt_downsample

        self.img_names=[filename for filename in os.listdir(img_root) \
                           if os.path.isfile(os.path.join(img_root,filename))]
        self.n_samples=len(self.img_names)

    def __len__(self):
        return self.n_samples

    def __getitem__(self, index):
      assert index <= len(self), 'index range error'
      img_name = self.img_names[index]
      img = plt.imread(os.path.join(self.img_root, img_name))
      print(img.shape)
      # Handle grayscale image case
      if len(img.shape) == 2:  # If image is grayscale
          img = img[:, :, np.newaxis]  # Expand dimensions
          img = np.concatenate((img, img, img), 2)  # Convert to 3 channels (RGB)

      gt_dmap = np.load(os.path.join(self.gt_dmap_root, img_name.replace('.jpg', '.npy')))
      print(gt_dmap.shape)
      # If downsampling is required
      if self.gt_downsample > 1:  
          ds_rows = int(img.shape[0] // self.gt_downsample)
          ds_cols = int(img.shape[1] // self.gt_downsample)
          img = cv2.resize(img, (ds_cols * self.gt_downsample, ds_rows * self.gt_downsample))
          gt_dmap = cv2.resize(gt_dmap, (ds_cols, ds_rows))

      # Convert to tensors
      img = img.transpose((2, 0, 1))  # Convert to (C, H, W) format for PyTorch
      gt_dmap = gt_dmap[np.newaxis, :, :]  # Add channel dimension to density map

      # Create tensors for PyTorch
      img_tensor = torch.tensor(img, dtype=torch.float)
      gt_dmap_tensor = torch.tensor(gt_dmap, dtype=torch.float)

      return img_tensor, gt_dmap_tensor


class MCNN(nn.Module):
    '''
    Implementation of Multi-column CNN for crowd counting
    '''
    def __init__(self,load_weights=False):
        super(MCNN,self).__init__()

        self.branch1=nn.Sequential(
            nn.Conv2d(3,16,9,padding=4),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(16,32,7,padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32,16,7,padding=3),
            nn.ReLU(inplace=True),
            nn.Conv2d(16,8,7,padding=3),
            nn.ReLU(inplace=True)
        )

        self.branch2=nn.Sequential(
            nn.Conv2d(3,20,7,padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(20,40,5,padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(40,20,5,padding=2),
            nn.ReLU(inplace=True),
            nn.Conv2d(20,10,5,padding=2),
            nn.ReLU(inplace=True)
        )

        self.branch3=nn.Sequential(
            nn.Conv2d(3,24,5,padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(24,48,3,padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(48,24,3,padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(24,12,3,padding=1),
            nn.ReLU(inplace=True)
        )

        self.fuse=nn.Sequential(nn.Conv2d(30,1,1,padding=0))

        if not load_weights:
            self._initialize_weights()

    def forward(self,img_tensor):
        x1=self.branch1(img_tensor)
        x2=self.branch2(img_tensor)
        x3=self.branch3(img_tensor)
        x=torch.cat((x1,x2,x3),1)
        x=self.fuse(x)
        return x

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.normal_(m.weight, std=0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

def cal_mae(img_root, gt_dmap_root, model_param_path):
    '''
    Calculate the MAE of the test data for all images in the dataset.
    img_root: the root of test image data.
    gt_dmap_root: the root of test ground truth density-map data.
    model_param_path: the path of specific mcnn parameters.
    '''
    device = torch.device("cpu")
    mcnn = MCNN().to(device)

    # Load the model parameters to CPU
    mcnn.load_state_dict(torch.load(model_param_path, map_location=torch.device('cpu')))

    dataset = CrowdDataset(img_root, gt_dmap_root, 1)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)
    mcnn.eval()
    mae = 0
    
    with torch.no_grad():
        for i, (img, gt_dmap) in enumerate(dataloader):
            img = img.to(device)
            gt_dmap = gt_dmap.to(device)
            # Forward propagation
            et_dmap = mcnn(img)
            
            original_shape = img.shape[2:]  # Store original shape
            if original_shape[0] % 4 == 0 and original_shape[1] % 4 == 0:
                # If both dimensions are multiples of 4, use cubic interpolation
                et_dmap = F.interpolate(et_dmap, scale_factor=4, mode='bicubic', align_corners=False)
            else:
                # Otherwise, resize directly to original shape
                et_dmap = F.interpolate(et_dmap, size=original_shape, mode='bilinear', align_corners=False)
            
            mae += abs(et_dmap.data.sum() - gt_dmap.data.sum()).item()
            del img, gt_dmap, et_dmap

    print("MAE of the entire dataset: " + str(mae / len(dataloader)))

def estimate_density_maps_for_all(img_root, gt_dmap_root, model_param_path, pred_dmap_root):
    '''
    Estimate density maps for all images and save them using the same filenames.
    img_root: the root of test image data.
    gt_dmap_root: the root of test ground truth density-map data.
    model_param_path: the path of specific mcnn parameters.
    pred_dmap_root: the directory where predicted density maps will be saved.
    '''
    device = torch.device("cpu")
    mcnn = MCNN().to(device)

    # Load the model parameters to CPU
    mcnn.load_state_dict(torch.load(model_param_path, map_location=torch.device('cpu')))

    dataset = CrowdDataset(img_root, gt_dmap_root, 1)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)

    mcnn.eval()

    os.makedirs(pred_dmap_root, exist_ok=True)  # Ensure output directory exists

    # Get list of image files to use their filenames for saving predicted density maps
    image_files = os.listdir(img_root)

    for i, (img, gt_dmap) in enumerate(dataloader):
        img = img.to(device)
        gt_dmap = gt_dmap.to(device)

        # Forward pass through the model
        et_dmap = mcnn(img).detach()
        original_shape = img.shape[2:]  # Store original shape
        if original_shape[0] % 4 == 0 and original_shape[1] % 4 == 0:
            # If both dimensions are multiples of 4, use cubic interpolation
            et_dmap = F.interpolate(et_dmap, scale_factor=4, mode='bicubic', align_corners=False)
        else:
            # Otherwise, resize directly to original shape
            et_dmap = F.interpolate(et_dmap, size=original_shape, mode='bilinear', align_corners=False)
        # Convert predicted density map to NumPy array
        et_dmap = et_dmap.squeeze(0).squeeze(0).cpu().numpy()

        # Use the same filename as the image or ground truth density map
        image_filename = image_files[i]
        base_filename = os.path.splitext(image_filename)[0]  # Remove the file extension

        # Save predicted density map as .npy and .png using the same name
        predicted_density_filename_npy = f"{base_filename}.npy"
        predicted_density_filename_png = f"{base_filename}.png"

        np.save(os.path.join(pred_dmap_root, predicted_density_filename_npy), et_dmap)

        # Save the predicted density map as an image
        plt.imshow(et_dmap, cmap='hot')
        plt.colorbar()

        # Save the image
        plt.savefig(os.path.join(pred_dmap_root, predicted_density_filename_png))
        plt.close()  # Close the plot to avoid overwriting issues

        print(f"Predicted density map saved as {predicted_density_filename_npy} and {predicted_density_filename_png}")

if __name__ == "__main__":
    torch.backends.cudnn.enabled = False

    # Define your paths
    img_root = 'dataset/val/images'
    gt_dmap_root = 'dataset/val/ground_truth'
    pred_dmap_root = 'dataset/val/dens'
    
    os.makedirs(pred_dmap_root, exist_ok=True)

    # Model parameter path
    model_param_path = 'model.param'
    
    # Calculate MAE for the entire dataset
    cal_mae(img_root, gt_dmap_root, model_param_path)
    
    # Estimate and save density maps for all images with the same filenames
    estimate_density_maps_for_all(img_root, gt_dmap_root, model_param_path, pred_dmap_root)
