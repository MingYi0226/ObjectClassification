from io import BytesIO
import cv2
import json
import torch
import torchvision
import numpy as np

from starlette.datastructures import UploadFile
from typing import List
from bbox import BBox2D, XYXY, XYWH, BBox2DList
from PIL import ImageOps, Image

class BBoxL:
    def __init__(self, bbox2d: BBox2D, label: str):
        self.bbox = bbox2d
        self.label = label
    
    def __hash__(self):
        return hash(f"{self.label}_{self.bbox.x1}_{self.bbox.y1}_{self.bbox.x2}_{self.bbox.y2}")

    def __eq__(self, other):
        return self.label == other.label and self.bbox.x1 == other.bbox.x1 and self.bbox.y1 == other.bbox.y1 and self.bbox.x2 == other.bbox.x2 and self.bbox.y2 == other.bbox.y2

class BBoxLS:
    def __init__(self, bbox2d: BBox2D, label: str, confidence: float):
        self.bbox = bbox2d
        self.label = label
        self.confidence = confidence
    
    def __hash__(self):
        return hash(f"{self.label}_{self.bbox.x1}_{self.bbox.y1}_{self.bbox.x2}_{self.bbox.y2}_{self.confidence}")

    def __eq__(self, other):
        return self.label == other.label and self.bbox.x1 == other.bbox.x1 and self.bbox.y1 == other.bbox.y1 and self.bbox.x2 == other.bbox.x2 and self.bbox.y2 == other.bbox.y2 and self.confidence == other.confidence

class Prediction():
    def __init__(self, inference_json):
        self.image_id = inference_json["image_id"]
        self.tray_id = inference_json["tray_id"]
        self.boxes: BBox2DList = BBox2DList([])
        self.scores: List[float] = []
        self.labels: List[str] = []
        self.data: List[BBoxLS] = []
        for pred_obj in inference_json["predictions"]:
            bbox2d = BBox2D([pred_obj["xmin"], pred_obj["ymin"], pred_obj["xmax"], pred_obj["ymax"]], mode=XYXY)
            self.boxes = self.boxes.append(bbox2d)
            self.scores.append(pred_obj["confidence_score"])
            self.labels.append(pred_obj["part_id"])
            self.data.append(BBoxLS(bbox2d, pred_obj["part_id"], pred_obj["confidence_score"]))

    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx) -> BBoxLS:
        return self.data[idx]
    
    def set_boxes(self, boxes: BBox2DList):
        self.boxes = boxes
        self.data = [BBoxLS(self.boxes[i], self.labels[i], self.scores[i]) for i in range(len(self.boxes))]
    
    def set_labels(self, labels: List[str]):
        self.labels = labels
        self.data = [BBoxLS(self.boxes[i], self.labels[i], self.scores[i]) for i in range(len(self.boxes))]
    
    def set_scores(self, scores: List[float]):
        self.scores = scores
        self.data = [BBoxLS(self.boxes[i], self.labels[i], self.scores[i]) for i in range(len(self.boxes))]
    
    def nms(self, nms_threshold=0.4):
        nms_indices = torchvision.ops.nms(
            torch.from_numpy(self.boxes.numpy(mode=XYXY)),
            torch.from_numpy(np.array(self.scores)), nms_threshold).numpy().tolist()
        self.boxes = BBox2DList([self.boxes[i] for i in nms_indices])
        self.scores = [self.scores[i] for i in nms_indices]
        self.labels = [self.labels[i] for i in nms_indices]
        self.data = [self.data[i] for i in nms_indices]

class Annotation():
    def __init__(self, annotation_json):
        self.image_id = annotation_json["fileName"]
        self.image_id = annotation_json["refTrayId"]
        self.boxes: BBox2DList = BBox2DList([])
        self.labels: List[str] = []
        self.data: List[BBoxL] = []
        for anno_obj in annotation_json["components"]:
            bbox2d = BBox2D([anno_obj["xMin"], anno_obj["yMin"], anno_obj["xMax"], anno_obj["yMax"]], mode=XYXY)
            self.boxes = self.boxes.append(bbox2d)
            self.labels.append(anno_obj["componentId"])
            self.data.append(BBoxL(bbox2d, anno_obj["componentId"]))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx) -> BBoxL:
        return self.data[idx]

    def set_boxes(self, boxes: BBox2DList):
        self.boxes = boxes
        self.data = [BBoxL(self.boxes[i], self.labels[i]) for i in range(len(self.boxes))]
    
    def set_labels(self, labels: List[str]):
        self.labels = labels
        self.data = [BBoxL(self.boxes[i], self.labels[i]) for i in range(len(self.boxes))]
    
class MatchedBBox():
    def __init__(self, annotation: BBoxL, prediction: BBoxLS):
        self.annotation: BBoxL = annotation
        self.prediction: BBoxLS = prediction
        self.iou = calculate_iou(annotation.bbox, prediction.bbox)

class MetricCollector():
    def __init__(self):
        self.correct = 0
        self.misclassified = 0
        self.critical_misclassifications = 0
        self.matched_bboxes: List[MatchedBBox] = []
        self.unmatched_bboxes: List[BBoxLS] = []
    
    def __add__(self, metrics):
        self.correct += metrics.correct
        self.misclassified += metrics.misclassified
        self.critical_misclassifications += metrics.critical_misclassifications
        self.matched_bboxes += metrics.matched_bboxes
        self.unmatched_bboxes += metrics.unmatched_bboxes
        return self

def calculate_iou(gt: BBox2D, pr: BBox2D) -> float:
    gt = gt.numpy(mode=XYXY)
    pr = pr.numpy(mode=XYXY)
    # Calculate overlap area
    dx = min(gt[2], pr[2]) - max(gt[0], pr[0]) + 1
    if dx < 0:
        return 0.0
    dy = min(gt[3], pr[3]) - max(gt[1], pr[1]) + 1
    if dy < 0:
        return 0.0
    overlap_area = dx * dy
    # Calculate union area
    union_area = (
            (gt[2] - gt[0] + 1) * (gt[3] - gt[1] + 1) +
            (pr[2] - pr[0] + 1) * (pr[3] - pr[1] + 1) -
            overlap_area
    )
    return overlap_area / union_area

def calc_dist(bbox_a: BBox2D, bbox_b: BBox2D) -> float:
    # calculate the position of the center of bbox_a
    center_x_a = bbox_a.x1 + bbox_a.w / 2
    center_y_a = bbox_a.y1 + bbox_a.h / 2
    # calculate the position of the center of bbox_b
    center_x_b = bbox_b.x1 + bbox_b.w / 2
    center_y_b = bbox_b.y1 + bbox_b.h / 2

    # calculate the Euclidean distance between the two centers
    dist = np.sqrt(((center_x_b - center_x_a) ** 2) + ((center_y_b - center_y_a) ** 2))
    return dist

def find_best_match(gts: BBox2DList, pred: BBox2D, threshold=0.25) -> int:
    best_match_iou = -np.inf
    best_match_idx = -1
    for gt_idx in range(len(gts)):
        iou = calculate_iou(gts[gt_idx], pred)
        if iou < threshold:
            continue
        if iou > best_match_iou:
            best_match_iou = iou
            best_match_idx = gt_idx
    return best_match_idx

def find_best_match_distiou(gts: BBox2DList, pred: BBox2D) -> int:
    best_match_dist = np.inf
    best_match_idx = -1
    for gt_idx in range(len(gts)):
        dist = calc_dist(gts[gt_idx], pred)
        if dist < best_match_dist:
            best_match_dist = dist
            best_match_idx = gt_idx
    if best_match_idx != -1 and calculate_iou(gts[best_match_idx], pred) <= 0:
        best_match_idx = -1
    return best_match_idx

def image_load(path_or_imagefile: str or UploadFile):
    if isinstance(path_or_imagefile, str):
        return ImageOps.exif_transpose(Image.open(path_or_imagefile)).convert('RGB')
    else:
        return ImageOps.exif_transpose(Image.open(BytesIO(path_or_imagefile.file.read()))).convert('RGB')

def json_load(path):
    with open(path, "r") as f:
        loaded_json = json.load(f)
    return loaded_json

def get_status(confidence_score, confidence_threshold, auto_type):
    match_confidence = confidence_threshold
    manual_confidence = confidence_threshold * 5 / 7
    if auto_type == "auto" or confidence_score < 0:
        if confidence_score > match_confidence:
            status = "Match"
        elif confidence_score < manual_confidence:
            status = "Missing"
        else:
            status = "Manual"
    else:
        status = "Manual"
    return status

def get_color(confidence_score, confidence_threshold, auto_type):
    green_confidence = confidence_threshold
    red_confidence = confidence_threshold * 5 / 7
    if auto_type == "auto" or confidence_score < 0:
        if confidence_score > green_confidence:
            color = '#6CC24A'
        elif confidence_score < red_confidence:
            color = '#CA001B'
        else:
            color = '#FF8200'
    else:
        color = '#FF8200'
    return color
    
def get_filename_safe(image: Image.Image) -> str:
    try:
        return image.filename
    except:
        return "unknown_image_file.jpg"