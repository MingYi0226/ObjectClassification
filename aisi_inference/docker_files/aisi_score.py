import os
import json
import time
import copy
import torch
import torchvision.transforms as T

from PIL import ImageOps, Image

import globals
from io import BytesIO
from ilogger import logger
from utils import image_load
from consolidation import consolidate_response, validate_consolidation_requirements


class InferenceAISI ():
    def __init__ (self, config, image_file=None, is_vpcx="yes"):
        self.initiated = False
        try:
            start_time = time.time()
            self.categories = None
            if is_vpcx == "yes":
                self.vpcx = True
            else:
                self.vpcx = False
            end_time = time.time()
            logger.info(f"Start Constructor with basic flags: {end_time-start_time}")
            
            start_time = time.time()
            self.img = image_load(image_file)
            self.orig_width, self.orig_height = self.img.size
            self.img = self.img.resize((1920, 1080), Image.Resampling.LANCZOS)
            end_time = time.time()
            logger.info(f"Image open time: {end_time-start_time}")
            
            start_time=time.time()
            self.image_file_name = image_file.filename
            self.tray_id = config["tray_id"]
            self.site_id = config["site_id"]
            self.requestid = config["request_id"]
            end_time = time.time()
            logger.info(f"pull trayid request id from config: {end_time-start_time}")
            
            start_time = time.time()
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
            end_time = time.time()
            logger.info(f"Get torch device: {end_time-start_time}")
            self.initiated = True
        except Exception as e:
            logger.error(f"Cannot create Inference instance: {e}")
    
    def core_score(self, model, categories):
        function_name = "core_score"
        try:
            logger.info(f"{function_name}: started")
            classes = tuple(categories.keys())

            model.to(self.device)
            model.eval()
            row = {}
            with torch.no_grad():
                self.img = ImageOps.exif_transpose(self.img)
                img = T.functional.to_tensor(self.img)
                img = [img.to(self.device)]
                prediction = model(img)
                
                row["image_id"] = self.image_file_name
                row["site_id"] = self.site_id
                row["tray_id"] = self.tray_id
                row["predictions"] = []
                for i,p in enumerate(prediction[0]["scores"]):
                    sub_row = {}
                    label = prediction[0]["labels"][i].cpu().numpy()
                    
                    sub_row["part_id"] = str(classes[label-1])
                    boxes = prediction[0]["boxes"][i].cpu().numpy()
                    sub_row['confidence_score'] = float(p.cpu().numpy())
                    sub_row['xmin']=int(boxes[0])
                    sub_row['ymin']= int(boxes[1])
                    sub_row['xmax'] = int(boxes[2])
                    sub_row['ymax'] = int(boxes[3])
                    row["predictions"].append(sub_row)
            return row, True
        except Exception as e:
            logger.error(f'{function_name}: failed: {e}')
            return {}, False

def get_model(target_group, device):
    function_name = "get_model"
    try:
        siteid = target_group["siteId"]
        trayid = target_group["trayId"]
        # if not exist
        if len(globals.groups) == 0 or target_group not in globals.groups:
            # get model path
            model_file_path = os.path.join(globals.output_path, siteid, trayid, trayid + ".pkl")

            # load model
            with open(model_file_path, 'rb') as fin:
                pkl_model = torch.load(fin, map_location=torch.device(device))
            
            # load categories json file
            categories_path = os.path.join(globals.output_path, siteid, trayid, "categories.json")
            with open(categories_path,"r") as cat_fin:
                categories_json = json.load(cat_fin)

            validation_status, autocompletion_metadata, ref_image_0, ref_anno_0, ref_image_180, ref_anno_180 = validate_consolidation_requirements(siteid, trayid)
            meta_data = (validation_status, autocompletion_metadata, ref_image_0, ref_anno_0, ref_image_180, ref_anno_180)
            
            # update array
            globals.models.append(pkl_model)
            globals.categories.append(categories_json)
            globals.groups.append(target_group)
            globals.meta_data.append(meta_data)
        else:
            index = globals.groups.index(target_group)
            pkl_model = globals.models[index]
            categories_json = globals.categories[index]
            meta_data = globals.meta_data[index]

        pkl_model.to(device)
        return pkl_model, categories_json, meta_data
    except Exception as e:
        logger.error(f'{function_name}: Can not load model:{e}')
    return None, None

def translate_to_orig_size(response, current_size, orig_size):
    cw, ch = current_size
    ow, oh = orig_size
    for i in range(len(response["predictions"])):
        response["predictions"][i]["xmin"] *= ow / cw
        response["predictions"][i]["ymin"] *= oh / ch
        response["predictions"][i]["xmax"] *= ow / cw
        response["predictions"][i]["ymax"] *= oh / ch
    return response

def score(config, image_file=None, is_vpcx="yes" ):
    function_name = "score"
    try:
        # First instance the class
        aisi = InferenceAISI(config, image_file=image_file, is_vpcx=is_vpcx)

        # failed to initiate the instance
        if not aisi.initiated:
            message = "ERROR: Something unexpected happened. Possibly the image is corrupted."
            logger.error(f"{function_name}: {message}")
            return {"message": message}

        # Verify that the combination belongs to this endpoint
        target_group = {
            "siteId": str(aisi.site_id), 
            "trayId":str(aisi.tray_id)
        }

        if len(globals.site_tray_comb_lst) == 0:
            message = "ERROR: The endpoint might have restarted. Ask MFlow ML team to configure site and tray combinations for endpoint."
            logger.error(f"{function_name}: {message}")
            return {"message": message}

        # get the index of (siteId, trayId)
        if target_group not in globals.site_tray_comb_lst:
            message = "ERROR: Site id and Tray id combination do not belong to this endpoint."
            logger.error(f"{function_name}: {message}")
            return {"message": message}
        idx = globals.site_tray_comb_lst.index(target_group)

        # validate index in semaphores
        if idx >= len(globals.semaphores):
            message = "ERROR: Site id and Tray id are not able to call."
            logger.error(f"{function_name}: {message}")
            return {"message": message}
        semaphore = globals.semaphores[idx]
        
        with semaphore:
            start_time = time.time()
            logger.info(f"{function_name}: Main Score started for {aisi.requestid}")

            # load model and categories
            pkl_model, categories_dict, meta_data = get_model(target_group, aisi.device)

            end_time = time.time()
            logger.info(f"{function_name}: Get model: {end_time-start_time}")

            if pkl_model is None or categories_dict is None:
                message = "ERROR:  Trained model and related information not found. Please train again."
                logger.error(f"{function_name}: {message}")
                return {"message": message}

            start_time =time.time()
            response, isSuccessed = aisi.core_score(pkl_model, categories_dict)
            end_time = time.time()
            logger.info(f"{function_name}: Core score: {end_time-start_time}")
            start_time =time.time()
            try:
                consolidated_response = consolidate_response(copy.deepcopy(response), aisi.img, meta_data)
                consolidated_response = translate_to_orig_size(consolidated_response, aisi.img.size, (aisi.orig_width, aisi.orig_height))
            except Exception as e:
                message = "Error in consolidation"
                logger.error(f"{function_name}: {message}: {e}")
                consolidated_response = copy.deepcopy(response)
            end_time = time.time()
            logger.info(f"{function_name}: consolidate_response: {end_time-start_time}")

            if not isSuccessed:
                message = "ERROR: Failed to predict"
                logger.error(f"{function_name}: {message}")
                return {"message": message}

            pkl_model.to('cpu')

            if globals.tracking_mode:
                infer_path_lst = globals.output_path.split('/')
                infer_path_lst[-1] = "inference"
                infer_path = "/".join(infer_path_lst)
                infer_path = os.path.join(infer_path, aisi.site_id, aisi.tray_id)
                os.makedirs(infer_path, exist_ok=True)
                
                infer_data = {
                    "requestid": aisi.requestid,
                    "response": consolidated_response,
                    "unconsolidated_response": response
                    }
                with open(os.path.join(infer_path, aisi.requestid + ".json"), "w") as f:
                    json.dump(infer_data, f)
            
            logger.info(f"{function_name}: Main Score done")
            return consolidated_response
    except Exception as e:
        logger.error(f'{function_name}: failed: {e}')
        return {"message": "ERROR: Failed to call score(). Ask Administrator."}
