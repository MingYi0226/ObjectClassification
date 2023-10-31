"""
Created by Suchitra Ganapathi
"""
import os
import random
import shutil
import numpy as np
import time
import json
import requests
import torch
import torchvision

from PIL import ImageFile, ImageOps, Image
from utils.CustomDataset import CustomDataset
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor, FasterRCNN	
from torchvision.models.detection.backbone_utils import resnet_fpn_backbone
from pytorch_coco.engine import train_one_epoch
from torch.utils.data import ConcatDataset
from utils.ilogger import logger
from utils.metrics import *
from pytorch_coco.utils import collate_fn
from utils.utils import *

ImageFile.LOAD_TRUNCATED_IMAGES = True

class AISI():
    def __init__(self,config, is_vpcx="yes"):
        function_name = "aisi_model.init"
        try:
            start_time = time.time()
            self.categories = None
            self.vpcx = True if is_vpcx == 'yes' else False
            end_time = time.time()
            logger.info(f"{function_name} - Start Constructor with basic flags: {end_time-start_time}")

            hyper_param = config.get('hyperparam',{})
            if isinstance(hyper_param, str):
                hyper_param = json.loads(hyper_param)    
            self.model_file_name = config['modelfilename']
            self.file_share_name = config['filesharename']
            self.file_share_pkl_folder_name = config['filesharepklfoldername']
            self.callbackurl = config.get('callbackurl')
            self.file_share_data_folder_name = config.get('modeldatafoldername')
            self.file_share_model_metrics_name = config.get('modelmatricsfoldername')
            self.model_metrics_file_name = config.get('modelmatricsfilename')
            self.lr = hyper_param.get("lr",0.005)
            self.momentum = hyper_param.get("momentum",0.9)
            self.weight_decay = hyper_param.get("weight_decay",0.0005)
            self.step_size = hyper_param.get("step_size",3)
            self.gamma = hyper_param.get("gamma",0.1)
            self.num_epochs = hyper_param.get("epochs",1)
            self.threshold = hyper_param.get("threshold", 0.7)
            self.tray_id = hyper_param["tray_id"]
            self.site_id = hyper_param["site_id"]
            self.training_folder = os.path.join(config.get("trainingdata"), self.site_id, self.tray_id, 'annotations')
            self.output_path = os.path.join(self.training_folder.split('/input')[0], 'output')
            self.repeat = hyper_param.get("repeat", 1)
            self.batch_size = hyper_param.get("batch_size", 2)
            # self.resize = hyper_param.get("resize", 1)
            self.isValid = self.validate_folders()

            if not self.isValid:
                raise Exception("trainset path is invalid")
            
            start_time=time.time()
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
            end_time = time.time()
            logger.info(f"{function_name} - torch device: {end_time-start_time}")
        except Exception as e:
            logger.error(f"{function_name} - Constructor err: {e}")
            callbackmessage = 'Please check if siteid, trayid is correct. Please check if files are downloaded correctly. Please contact MFlow team for further assistance.'
            logger.error(f"{function_name} - {callbackmessage}")
            self.report(False, callbackmessage)
        
    def validate_folders(self):
        function_name = "aisi_model.validate_folders"
        training_data_present = False
        try:
            if self.training_folder and self.training_folder != "":
                if os.path.exists(self.training_folder):
                    logger.info(f"{function_name} - {self.training_folder} found")
                    training_data_present = True
            if not training_data_present:
                logger.warning(f"{function_name} - {self.training_folder} Not found")
                callbackmessage = 'Training data is not found in cloud storage. Please make sure Download endpoint of SAA API was called before starting training.'
                logger.warning(f"{function_name} - {callbackmessage}")
                self.report(False, callbackmessage)
        except Exception as e:
            logger.error(f"{function_name} - validate_folders err: {e}")
        return training_data_present

    def create_dataloaders(self):
        function_name = "aisi_model.create_dataloaders"
        is_successed = False
        try:
            logger.info(f"{function_name} - Creating dataloaders")
            tray_annotations = list(os.listdir(self.training_folder))
            self.categories = self.get_categories_dict(tray_annotations, self.training_folder)

            # if failed to get categories
            if len(self.categories) == 0:
                logger.error(f"{function_name} - No valid categories")
                return is_successed

            self.classes = tuple(self.categories.keys())

            # Randomly shuffle the tray_annotations list
            random.shuffle(tray_annotations)

            # split train & valid annotations
            split_rate = .80 # This will be converted to a parameter in the future
            split_ele = int(len(tray_annotations)*split_rate)
            train_trays = tray_annotations[:split_ele]
            val_trays = tray_annotations[split_ele:]

            dataset_train_list = []
            temp_dataset = CustomDataset(self.training_folder, train_trays, self.categories, transforms= None)
            for i in range(self.repeat):
                dataset_train_list.append(temp_dataset)

            dataset_valid = CustomDataset(self.training_folder, val_trays, self.categories, transforms= None)
            dataset_train = ConcatDataset(dataset_train_list)
            
            data_loader_train = torch.utils.data.DataLoader(
                        dataset_train, batch_size=self.batch_size , shuffle=True, collate_fn=collate_fn)
            is_successed = True
        except Exception as e:
            logger.error(f"{function_name} - create_dataloaders err: {e}")
        return is_successed, data_loader_train, dataset_valid

    def get_categories_dict(self, tray_annotations, root_tray_path):
        function_name = "aisi_model.get_categories_dict"
        categories = []
        try:
            for annotation in tray_annotations:
                with open(os.path.join(root_tray_path, annotation)) as f:
                    data = json.load(f)
                # Get all categories
                categories.extend([comp['componentId'] for comp in data['components']]) 
            categories_dict = {k:v+1 for v,k in enumerate(set(categories))}
        except Exception as e:
            logger.error(f"{function_name} - get_categories_dict err:{e}")
        return categories_dict

    def create_output_structure_and_backup(self):
        function_name = "aisi_model.create_output_structure_and_backup"
        try:
            out_folder = os.path.join(self.output_path, self.site_id ,self.tray_id)
            os.makedirs(os.getcwd()+'/output/', exist_ok=True)
            os.makedirs(out_folder, exist_ok=True)
            if os.path.exists(os.path.join(out_folder, 'backup')):
                shutil.rmtree(os.path.join(out_folder, 'backup'))
            os.makedirs(os.path.join(out_folder, 'backup'), exist_ok=True)
            
            for f in os.listdir(out_folder):
                if os.path.isdir(os.path.join(out_folder, f)):
                    continue
                os.rename(os.path.join(out_folder, f), os.path.join(out_folder, 'backup', f))
        except Exception as e:
            logger.error(f"{function_name} - create_output_structure_and_backup err: {e}")
            raise Exception('create_output_structure_and_backup err')

    def core_train(self, data_loader_train):
        function_name = "aisi_model.core_train"
        try:
            logger.info(f"{function_name} - Core training started")
            
            backbone = resnet_fpn_backbone('resnet101', pretrained=True)	
            num_classes = len(self.classes)+1	
            model = FasterRCNN(backbone, num_classes=num_classes)
            in_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes).to(self.device) 

            # construct an optimizer
            for param in model.parameters():
                param.requires_grad = True
                
            # construct an optimizer
            params = [p for p in model.parameters() if p.requires_grad]
            optimizer = torch.optim.SGD(params, lr=self.lr,
                                        momentum=self.momentum, weight_decay=self.weight_decay)
            lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                        step_size=self.step_size,
                                                        gamma=self.gamma)

            for epoch in range(self.num_epochs):
                # train for one epoch, printing every 10 iterations
                train_one_epoch(model, optimizer, data_loader_train, self.device, epoch, print_freq=10)
                # update the learning rate
                lr_scheduler.step()
            
            logger.info(f"{function_name} - Core Training done")
            return model
        except Exception as e:
            logger.error(f"{function_name} - core_train err:{e}")
        return None

    def compute_metrics(self, model, dataloader, threshold=0.7):
        function_name = "aisi_model.compute_metrics"
        try:
            model.eval()
            tp_list = []
            target_labels_list = []
            scores_list = []
            labels_list = []
            iou_list = []
            size = 0
            with torch.no_grad():        
                for index, (imgs,targets) in enumerate(dataloader):
                    imgs = list(img.to(self.device) for img in imgs)
                    predictions = model(imgs)
                    size += index
                    for i, prediction in enumerate(predictions):
                        target = targets[i]
                        boxes = []
                        scores = []
                        labels = []
                        for i,p in enumerate(prediction["scores"]):
                            if p>threshold:
                                boxes.append(prediction["boxes"][i].cpu().numpy())
                                scores.append(prediction["scores"][i].cpu().item())
                                labels.append(prediction["labels"][i].cpu().item())
                        labels_np = np.array(labels)
                        scores_np = np.array(scores)
                    tp, labels, scores, iou = compute_tp(target["boxes"].cpu().numpy(), 
                                    target["labels"].cpu().numpy(),
                                    boxes, labels, labels_np, scores_np, iou_threshold=0.5)
                    
                    scores_list.extend(scores)
                    labels_list.extend(labels)
        
                    target_labels_list.extend(target["labels"])
                    tp_list.extend(tp)
                    iou_list.extend(iou)
            logger.debug(f"{function_name} - tp list: {tp_list}, length of tp_list: {len(tp_list)}\nlabels list: {labels_list}, length of labels_list: {len(labels_list)}\nscores list: {scores_list}, length of scores_list: {len(scores_list)}")
            
            p, r, ap, f1, unique_labels =  ap_per_class(
                                            np.asarray(tp_list), 
                                            np.asarray(scores_list),
                                            np.asarray(labels_list), 
                                            np.asarray(target_labels_list))
            
            return np.mean(ap), np.mean(iou_list)
        except Exception as e:
            logger.error(f"{function_name} - compute_metrics err:{e}")
        return -1, -1

    def evaluate(self, model, dataset_valid):
        function_name = "aisi_model.evaluate"
        res = False
        try:
            logger.info(f"{function_name} - Evaluating model")

            data_loader_valid = torch.utils.data.DataLoader(
                        dataset_valid, batch_size=1, shuffle=False, collate_fn=collate_fn)

            m_AP, iou = self.compute_metrics(model, data_loader_valid, self.threshold)
            if m_AP < 0 and iou < 0:
                raise Exception('compute_metrics result is invalid.')
        
            logger.info(f"{function_name} - tray_id: {self.tray_id}, m_AP: {m_AP:.2f}, iou: {iou:.2f}")

            logger.info(f"{function_name} - Saving metrics and model")
            with open(os.getcwd()+'/output/'+ self.model_metrics_file_name, 'w') as metrics_file:
                metrics_json = []
                metrics_json.append(
                    {
                        'tray_id': self.tray_id,
                        'validation mAP': m_AP,
                        "validation iou": iou
                    }
                )
                json.dump(
                    metrics_json, metrics_file
                )

            with open(os.getcwd()+'/output/'+ self.model_file_name, 'wb') as fout:
                torch.save(model, fout)

            logger.info(f"{function_name} - Evaluating model done and model saved")
            res = True
        except Exception as e:
            logger.error(f"{function_name} - evaluate err:{e}")
            raise Exception(f"{function_name} - Model evaluate err")
        return res

    def report(self, status, callbackmessage):
        function_name = "aisi_model.report"
        try:
            str_status = "true" if status else "false"
            str_json = "{status: " + str_status + ", message: '"+callbackmessage + "'}"
            if self.vpcx:
                res = requests.post(self.callbackurl, json=str_json, verify=False)
            else:
                res = requests.post(self.callbackurl, json=str_json)
            logger.debug(f"{function_name} - url: {self.callbackurl}, res: {res}, {res.text}")
        except Exception as e:
            logger.error(f"{function_name} - report err: {e}")

    def copy_files(self, model_path, metrics_path):
        try:
            # copy model
            pkl_file = os.getcwd() + '/output/' + self.model_file_name
            shutil.copyfile(pkl_file, model_path)

            # copy metrics
            metrics_file = os.getcwd() + '/output/'+ self.model_metrics_file_name
            shutil.copyfile(metrics_file, metrics_path)
            return True
        except Exception as e:
            logger.debug(f'Failed to copy files to {model_path} and {metrics_path}: {e}')
            return False

    def copy_reference_data(self, base_path, site_id, tray_id):
        res = False
        try:
            output_path = os.path.join(base_path, "output")
            img_path = os.path.join(base_path, 'input', site_id, tray_id, "images")
            ann_path = os.path.join(base_path, 'input', site_id, tray_id, "annotations")
            
            file_list = sorted(os.listdir(img_path))
            if len(file_list) == 0:
                raise Exception(f'ERROR=> site_id: {site_id} tray_id: {tray_id} : images not found')
                
            # copy 0 degree image
            first_name = file_list[0]
            src_path = os.path.join(img_path, first_name)

            dst_dir = os.path.join(output_path, site_id, tray_id, "reference", "images") 
            os.makedirs(dst_dir, exist_ok=True)
            
            img = Image.open(src_path).convert("RGB")
            img = ImageOps.exif_transpose(img)
            dst_path_0 = os.path.join(dst_dir, "reference_image_0.jpg")
            dst_img_path_180 = os.path.join(dst_dir, "reference_image_180.jpg")
            img.save(dst_path_0)
            logger.debug(f'{src_path} => {dst_path_0}')

            # copy 0 degree annotation
            first_name = first_name[:-4] + ".json"
            src_path = os.path.join(ann_path, first_name)

            dst_dir = os.path.join(output_path, site_id, tray_id, "reference", "annotations")
            os.makedirs(dst_dir, exist_ok=True)
            
            dst_path_0 = os.path.join(dst_dir, "reference_annotation_0.json")
            dst_json_path_180 = os.path.join(dst_dir, "reference_annotation_180.json")
            with open(src_path, 'r') as fr, open(dst_path_0, 'w') as fw0:
                json_data_0 = json.load(fr)
                json.dump(json_data_0, fw0, indent=4)
            logger.debug(f'{src_path} => {dst_path_0}')

            # get top-left component id
            categories = [comp['componentId'] for comp in json_data_0["components"] if comp['componentId']]
            
            top_left_id = get_top_left_comp(json_data_0, categories)
            if not top_left_id:
                raise Exception(f'ERROR=> site_id: {site_id} tray_id: {tray_id} : top-left component not found')
                
            first_comp_pos = get_compo_pos(json_data_0, top_left_id)
            if first_comp_pos < 0:
                raise Exception(f'ERROR=> site_id: {site_id} tray_id: {tray_id} : top-left component invalid')
                
            logger.debug(f'top left component: {top_left_id}, {first_comp_pos}')

            is_180_found = False
            json_data_180 = {}
            image_path_180 = ''
            current_file_name = file_list[0]
            for file_name in file_list[1:]:
                if compare_strings(current_file_name, file_name) <= 2:
                    current_file_name = file_name
                    continue
                current_file_name = file_name

                tmp_path = os.path.join(ann_path, file_name[:-4] + ".json")
                with open(tmp_path, 'r') as fr:
                    json_data_tmp = json.load(fr)
                new_pos = get_compo_pos(json_data_tmp, top_left_id)
                if new_pos < 0:
                    continue
                logger.debug(f'{file_name} - {top_left_id} - {new_pos}')
                if new_pos == first_comp_pos:
                    continue
                is_180_found = True
                logger.debug(f'First 180 image found: {file_name}')
                json_data_180 = json_data_tmp
                image_path_180 = os.path.join(img_path, file_name)
                break

            if is_180_found:
                # save found image as 180-degre image
                shutil.copyfile(image_path_180, dst_img_path_180)
                # save found json as 180-degree annotation
                with open(dst_json_path_180, 'w') as fw0:
                    json.dump(json_data_180, fw0, indent=4)
            else:
                logger.debug("180 degree image was not found, will rotate 0-degree image")
                # save 180 degree rotated image
                img.rotate(180).save(dst_img_path_180)
                logger.debug(f'{src_path} => {dst_img_path_180}')

                # save 180 degree rotated annotation
                width = json_data_0["width"]
                height = json_data_0["height"]
                for i, comp in enumerate(json_data_0["components"]):
                    x1 = width - comp["xMax"]
                    y1 = height - comp["yMax"]
                    x2 = width - comp["xMin"]
                    y2 = height - comp["yMin"]

                    json_data_0["components"][i]["xMin"] = x1
                    json_data_0["components"][i]["yMin"] = y1
                    json_data_0["components"][i]["xMax"] = x2
                    json_data_0["components"][i]["yMax"] = y2

                with open(dst_json_path_180, 'w') as fw180:
                    json.dump(json_data_0, fw180, indent=4)
                logger.debug(f'{src_path} => {dst_json_path_180}')

            logger.debug(f'site_id: {site_id} tray_id: {tray_id} processed successfully')
            res = True
        except Exception as e:
            logger.error(f"copy_reference_image:{e}")
        return res

    def train(self):
        function_name = "aisi_model.train"
        res = False
        try:
            self.create_output_structure_and_backup()
            base_path = self.training_folder.split('/input')[0]
            
            is_successed = self.copy_reference_data(base_path, self.site_id, self.tray_id)
            if not is_successed:
                raise Exception("copy reference data failed")

            is_successed, data_loader_train, dataset_valid = self.create_dataloaders()
            if not is_successed:
                raise Exception("create datasets failed")
            
            model = self.core_train(data_loader_train)
            
            if model is None:
                raise Exception("failed to core_train()")

            if not self.evaluate(model, dataset_valid):
                raise Exception("failed to evaluate()")

            pkl_file_output_path = os.path.join(self.output_path, self.site_id, self.tray_id, self.tray_id+".pkl")
            metrics_output_path = os.path.join(self.output_path, self.site_id, self.tray_id, self.tray_id+".json")
            if not self.copy_files(pkl_file_output_path, metrics_output_path):
                raise Exception("failed to copy pkl and metrics file to output path")

            categories_path = os.path.join(self.output_path, self.site_id, self.tray_id, "categories.json")
            with open(categories_path,"w") as f:
                json.dump(self.categories, f)

            pkl_file_mflow_path = os.path.join("/",
                                                self.file_share_name,
                                                self.file_share_pkl_folder_name,
                                                self.model_file_name)
            metrics_mflow_path = os.path.join("/",
                                                self.file_share_name,
                                                self.file_share_model_metrics_name,
                                                self.model_metrics_file_name)
            if not self.copy_files(pkl_file_mflow_path, metrics_mflow_path):
                raise Exception("failed to copy pkl and metrics file to MFlow file share")

            callbackmessage = 'model training completed successsfully'
            logger.info(f"{function_name} - model training completed successsfully")
            res = True
        except Exception as e:
            callbackmessage = 'Exception occured. Please contact MFlow team'
            logger.error(f'{function_name} - train err:{e}')

        self.report(res, callbackmessage)
        
        return res