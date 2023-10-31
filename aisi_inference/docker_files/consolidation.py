import os
import cv2
import copy
import numpy as np

import globals
from ilogger import logger
from typing import List, Tuple
from bbox import BBox2D, XYXY, BBox2DList
from utils import BBoxL, MatchedBBox, Prediction, Annotation, BBoxLS, calc_dist, calculate_iou, find_best_match_distiou, get_color, get_status, image_load, json_load


def validate_consolidation_requirements(site_id, tray_id):
    function_name = "validate_consolidation_requirements"
    autocompletion_metadata_path = os.path.join(globals.output_path.replace("output", "input"), site_id, tray_id, "autocompletion", "autocompletion_metadata.json")
    ref_image_0_path = os.path.join(globals.output_path, site_id, tray_id, "reference", "images", "reference_image_0.jpg")
    ref_anno_0_path = os.path.join(globals.output_path, site_id, tray_id, "reference", "annotations", "reference_annotation_0.json")
    ref_image_180_path = os.path.join(globals.output_path, site_id, tray_id, "reference", "images", "reference_image_180.jpg")
    ref_anno_180_path = os.path.join(globals.output_path, site_id, tray_id, "reference", "annotations", "reference_annotation_180.json")
    path_exists = [
        os.path.exists(autocompletion_metadata_path),
        os.path.exists(ref_image_0_path),
        os.path.exists(ref_anno_0_path),
        os.path.exists(ref_image_180_path),
        os.path.exists(ref_anno_180_path)
    ]
    if not all(path_exists):
        logger.error(f"{function_name}: Consolidation files not found, unconsolidated response returned")
        return False, None, None, None, None, None
    autocompletion_metadata = json_load(autocompletion_metadata_path)
    ref_image_0 = image_load(ref_image_0_path)
    ref_anno_0 = json_load(ref_anno_0_path)
    ref_image_180 = image_load(ref_image_180_path)
    ref_anno_180 = json_load(ref_anno_180_path)
    logger.info(f"{function_name}: Consolidation files found, loading successful")
    return True, autocompletion_metadata, ref_image_0, ref_anno_0, ref_image_180, ref_anno_180

def match_template(preds: Prediction, annos: Annotation) -> Tuple[List[MatchedBBox], List[BBoxLS]]:
    matched = []
    unmatched = []
    matched_indices = {}
    for i in range(len(preds)):
        pred_bboxls: BBoxLS = preds[i]
        best_idx = find_best_match_distiou(annos.boxes, pred_bboxls.bbox)
        if best_idx != -1:
            if best_idx not in matched_indices:
                matched.append(MatchedBBox(annos.data[best_idx], pred_bboxls))
                matched_indices[best_idx] = len(matched) - 1
            else:
                prev_match_idx = matched_indices[best_idx]
                prev_matched = matched[prev_match_idx]
                prev_dist = calc_dist(prev_matched.prediction.bbox, prev_matched.annotation.bbox)
                prev_iou = calculate_iou(prev_matched.prediction.bbox, prev_matched.annotation.bbox)
                current_dist = calc_dist(pred_bboxls.bbox, annos.boxes[best_idx])
                current_iou = calculate_iou(pred_bboxls.bbox, annos.boxes[best_idx])
                
                if current_dist <= prev_dist and current_iou <= prev_iou:
                    unmatched.append(matched[prev_match_idx].prediction)
                    matched[prev_match_idx] = MatchedBBox(annos.data[best_idx], pred_bboxls)
                else:
                    unmatched.append(pred_bboxls)
        else:
            unmatched.append(pred_bboxls)
    return matched, unmatched

def get_feature_matches(img, refimg, thresh=0.7):
    function_name = "get_feature_matches"
    _img = cv2.cvtColor(np.array(copy.deepcopy(img)), cv2.COLOR_BGR2GRAY)
    _refimg = cv2.cvtColor(np.array(copy.deepcopy(refimg)), cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(_img, None)
    kp2, des2 = sift.detectAndCompute(_refimg, None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des2, des1, k=2)
    matches = list(filter(lambda m:  m[0].distance < thresh * m[1].distance, matches))
    matches = list(map(lambda m: m[0], matches))
    src_pts = np.float32([kp2[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp1[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    logger.debug(f"{function_name}: Good matches: {len(matches)}")
    return matches, src_pts, dst_pts

def get_translated_bbox(src_pts: BBox2D, M) -> BBox2D:
    if M is None:
        return src_pts
    # format the top left and bottom right corners of the bounding box coordinates
    src_pts_formatted = np.float32([[src_pts.x1, src_pts.y1], [src_pts.x2, src_pts.y2]]).reshape(-1, 1, 2)

    # get the transformed bounding box coordintates
    dst_pts = cv2.perspectiveTransform(src_pts_formatted, M)
    dst_pts = dst_pts.flatten()
    # identify the min_x, min_y, max_x and max_y coordinates for the transformed bounding box
    return BBox2D([
        min(dst_pts[0], dst_pts[2]),
        min(dst_pts[1], dst_pts[3]),
        max(dst_pts[0], dst_pts[2]),
        max(dst_pts[1], dst_pts[3])
        ], mode=XYXY)

def autocompletion_metadata_pass(inference_json, autocompletion_metadata):
    autocompletion_metadata_dict = {}
    for component in autocompletion_metadata["components"]:
        autocompletion_metadata_dict[component["componentId"]] = {
            "confidence_threshold": component["confidence_threshold"],
            "auto_type": component["auto_type"],
            "sub_type": component["sub_type"]
        }
    for i, pred in enumerate(inference_json["predictions"]):
        inference_json["predictions"][i]["color"] = get_color(
            pred["confidence_score"],
            autocompletion_metadata_dict[pred["part_id"]]["confidence_threshold"],
            autocompletion_metadata_dict[pred["part_id"]]["auto_type"]
        )
        inference_json["predictions"][i]["status"] = get_status(
            pred["confidence_score"],
            autocompletion_metadata_dict[pred["part_id"]]["confidence_threshold"],
            autocompletion_metadata_dict[pred["part_id"]]["auto_type"]
        )
    return inference_json

def add_missing_boxes(inference_parsed_json, unmatched_reference_bboxes: List[BBoxL]):
    function_name = "add_missing_boxes"
    logger.info(f"{function_name}: unmatched_reference_bboxes => {len(unmatched_reference_bboxes)}")
    for bboxl in unmatched_reference_bboxes:
        inference_parsed_json["predictions"].append({
            "xmin": bboxl.bbox.x1,
            "ymin": bboxl.bbox.y1,
            "xmax": bboxl.bbox.x2,
            "ymax": bboxl.bbox.y2,
            "confidence_score": -1,
            "part_id": bboxl.label
        })
    return inference_parsed_json

def qty_addition_pass(inference_parsed_json):
    for i in range(len(inference_parsed_json["predictions"])):
        comp_id = inference_parsed_json["predictions"][i]["part_id"]
        num_parts = len(list(filter(lambda x: x["part_id"] == comp_id and x["status"] != "Missing", inference_parsed_json["predictions"])))
        inference_parsed_json["predictions"][i]["qty"] = num_parts
    return inference_parsed_json

def consolidate_response(inference_response, image, meta_data):
    function_name = "consolidate_response"
    logger.info(f"{function_name}: Consolidation Started")
    validation_status, autocompletion_metadata, ref_image_0, ref_anno_0, ref_image_180, ref_anno_180 = meta_data # validate_consolidation_requirements(inference_response["site_id"], inference_response["tray_id"])
    if not validation_status:
        return inference_response
    pred = Prediction(inference_response)
    ref_anno_0 = Annotation(ref_anno_0)
    ref_anno_180 = Annotation(ref_anno_180)

    logger.info(f"{function_name}: Applying NMS")
    pred.nms(0.3)

    logger.info(f"{function_name}: Computing feature Matches")
    matches_ref1 = get_feature_matches(image, ref_image_0)
    matches_ref2 = get_feature_matches(image, ref_image_180)
    
    if len(matches_ref1[0]) > len (matches_ref2[0]):
        matches, src_pts, dst_pts = matches_ref1
        ref_anno = ref_anno_0
    else:
        matches, src_pts, dst_pts = matches_ref2
        ref_anno = ref_anno_180
    
    logger.info(f"{function_name}: Computing Homography Matrix")
    homography, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    logger.info(f"{function_name}: Translating Reference Boxes")
    ref_anno.set_boxes(BBox2DList([get_translated_bbox(ref_anno_bbox, homography) for ref_anno_bbox in ref_anno.boxes]))
    logger.info(f"{function_name}: Matching Reference Boxes to Predictions")
    matched, unmatched = match_template(pred, ref_anno)
    logger.info(f"{function_name}: Filtering Unmathced Bounding Boxes")
    matched_bboxls: List[BBoxL] = [m.annotation for m in matched]
    unmatched_reference_bboxes: List[BBoxL] = list(filter(lambda x: x not in matched_bboxls, ref_anno.data))
    filtered_preds: List[BBoxLS] = [m.prediction for m in matched]
    inference_response["predictions"] = [
        {
            "xmin": bboxls.bbox.x1,
            "ymin": bboxls.bbox.y1,
            "xmax": bboxls.bbox.x2,
            "ymax": bboxls.bbox.y2,
            "confidence_score": bboxls.confidence,
            "part_id": bboxls.label
        }
        for bboxls in filtered_preds]
    logger.info(f"{function_name}: Adding Missing Boxes")
    inference_layout_matched = add_missing_boxes(inference_response, unmatched_reference_bboxes)
    logger.info(f"{function_name}: Autocomplete Metadata Pass")
    metadata_added_preds = autocompletion_metadata_pass(inference_layout_matched, autocompletion_metadata)
    logger.info(f"{function_name}: Adding Component Quantity")
    qty_complete_preds = qty_addition_pass(metadata_added_preds)
    logger.info(f"{function_name}: Consolidation Complete")
    return qty_complete_preds
