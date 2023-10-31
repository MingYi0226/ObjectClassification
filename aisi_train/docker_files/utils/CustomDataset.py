import torch
import json
import os
from PIL import Image
import torchvision.transforms as T

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, root, annot_list, categories_dict, transforms):
        """
        args:
        root: The root folder of the annotations
        """
        self.root = root
        self.img_root = root.replace('annotations', 'images')
        self.transforms = transforms
        self.categories_dict = categories_dict
        self.annot_list = annot_list

    def __getitem__(self, idx):

        annot_path = os.path.join(self.root, self.annot_list[idx])
        

        # It is one json per image, so we need to load them one by one
        with open(annot_path, 'r') as f:
            annot = json.load(f)
        img_name = annot['fileName'].split('/')[-1]
        img_path = os.path.join(self.img_root, img_name)
        img = Image.open(img_path).convert("RGB")
        boxes = []
        labels = []
        num_objs = len(annot["components"])
        for bbox in annot["components"]:
            # This is only because the componentId is in a string format
            label = self.categories_dict[bbox["componentId"]]
            xmin = bbox["xMin"]
            ymin = bbox["yMin"]
            xmax = bbox["xMax"]
            ymax = bbox["yMax"]

            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(label)
        
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)

        image_id = torch.tensor([idx])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        # suppose all instances are not crowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd
        img = T.functional.to_tensor(img)

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.annot_list)
