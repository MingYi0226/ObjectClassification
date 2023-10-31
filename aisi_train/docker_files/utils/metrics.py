import numpy as np
from sklearn.metrics import confusion_matrix 
import tqdm

from utils.ilogger import logger

def create_masks(width,height,boxes):
    '''
    create mask around bounding boxes of image

    Args:
    width: REQUIRED, width of image
    height: REQUIRED, height of image
    boxes: REQUIRED, array of bounding boxes

    Return value: numPy array, masks around bounding boxes of image
    '''
    arr = np.array([[0]* width for i in range(height)])
    for xmin,ymin,xmax,ymax in boxes:
        arr[ymin:ymax,xmin:xmax] = 1
    return arr

def compute_metrics(y_pred,y_true):
    '''
    compute iou, dice coefficient and iou of mean positive and mean negative, averaged

    Args:
    y_pred: REQUIRED, array of predicted values
    y_true: REQUIRED, array of true values

    Return value: tuple containing iou, dice_coeff, and iou_pos_neg
    '''
    function_name = "metrics.compute_metrics"
    # reshape y_pred and y_true to be 1-dimensional arrays
    y_pred_r = y_pred.reshape(y_pred.shape[0]*y_pred.shape[1]) 
    y_true_r = y_true.reshape(y_true.shape[0]*y_true.shape[1])
    iou = 0
    dice_coeff = 0
    iou_pos_neg = 0
    current = confusion_matrix(y_true_r, y_pred_r, labels=[0, 1])
    logger.debug(f"{function_name} - confusion_matrix: {current}")
    tp = current[1][1]
    fp = current[0][1]
    fn = current[1][0]
    tn = current[0][0]
    
    if tp == 0 and fp == 0 and fn == 0:
        return 1.0, 1.0, 1.0 # iou=1, dice_coeff=1, iou_pos_neg=1
    #iou_pos_ne
    mean_pos = 0
    mean_neg = 0
    if tn+fp+fn != 0:
      mean_neg = tn/(tn+fp+fn)
    if tp+fn+fp != 0:
      mean_pos = tp/(tp+fp+fn)
    iou_pos_neg += (mean_pos+mean_neg)/2
    
    #iou_pos
    if tp+fn == 0 and tp+fp == 0:
      return iou, dice_coeff, iou_pos_neg
    iou_denominator = tp + fp+fn
    
    if iou_denominator !=0 :
      iou += tp / float(iou_denominator)
    
    #dice
    dice_denominator = (2*tp + fp+fn)
    
    if dice_denominator !=0 :
      dice_coeff += 2*tp / dice_denominator
      
    return iou, dice_coeff, iou_pos_neg
  
def bbox_iou(box1, box2):
    """
    Returns the IoU of two bounding boxes

    Args: 
    box1: REQUIRED, array of dimensions of box 1
    box2: REQUIRED, array of dimensions of box 2

    Return value: float, iou of 2 bounding boxes
    """
    # Get the coordinates of bounding boxes
    b1_x1, b1_y1, b1_x2, b1_y2 = box1[:, 0], box1[:, 1], box1[:, 2], box1[:, 3]
    b2_x1, b2_y1, b2_x2, b2_y2 = box2[:, 0], box2[:, 1], box2[:, 2], box2[:, 3]
    
    # get the corrdinates of the intersection rectangle
    inter_rect_x1 = np.maximum(b1_x1, b2_x1)
    inter_rect_y1 = np.maximum(b1_y1, b2_y1)
    inter_rect_x2 = np.minimum(b1_x2, b2_x2)
    inter_rect_y2 = np.minimum(b1_y2, b2_y2)
    
    # Intersection area
    inter_area = np.clip(inter_rect_x2 - inter_rect_x1 + 1, 0, None) * np.clip(
        inter_rect_y2 - inter_rect_y1 + 1, 0, None
    )
    # Union Area
    b1_area = (b1_x2 - b1_x1 + 1) * (b1_y2 - b1_y1 + 1)
    b2_area = (b2_x2 - b2_x1 + 1) * (b2_y2 - b2_y1 + 1)
    iou = inter_area / (b1_area + b2_area - inter_area + 1e-16)
    return iou

def compute_tp(target_boxes, target_labels, pred_boxes, pred_labels, pred_cls, conf, iou_threshold=0.5):
    '''
    calculate true positives, align pred labels and conf scores with true positives indexes, IoUs of bounding boxes

    Args:
    target_boxes: REQUIRED, array of target boxes
    target_labels: REQUIRED, array of target labels
    pred_boxes: REQUIRED, array of prediction boxes
    pred_labels: REQUIRED, array of prediction labels
    pred_cls: REQUIRED, array of predicted object classes
    conf: REQUIRED, array of objectness value ranging from 0-1
    iou_threshold: OPTIONAL, float, threshold of min iou, default - iou_threshold=0.5

    Return value: array of true positives, new_pred_cls, new_conf, iou_return_arr 
    '''
    function_name = "metrics.compute_tp"
    avg_iou = 0

    # all three will be set to length of target_labels
    true_positives = np.zeros(len(target_labels))
    new_pred_cls = np.full(len(target_labels), -1)
    new_conf = np.zeros(len(target_labels))

    false_positives = 0
    detected_boxes = []
    iou_return_arr = np.zeros(len(target_labels))
    # pred_i_lst = []


    for pred_i, pred_label in enumerate(pred_labels):
        # Ignore if label is not one of the target labels
        if pred_label not in target_labels:
            logger.debug(f"{function_name} - {pred_label}")
            false_positives += 1 # if pred label is not present in target labels, indicates that it is a fp, increment 1 to fp count
            continue
        
        pred_box = np.array([pred_boxes[pred_i][0], 
                             pred_boxes[pred_i][1], 
                             pred_boxes[pred_i][2], 
                             pred_boxes[pred_i][3]])
        iou_list=bbox_iou(np.expand_dims(pred_box,0), target_boxes) # calculate iou between prediction and target box
        
        box_index = np.argmax(iou_list)
        iou = iou_list[box_index]
        if iou >= iou_threshold and box_index not in detected_boxes and pred_label == target_labels[box_index] and pred_i < len(true_positives):
            true_positives[pred_i] = 1
            new_pred_cls[pred_i] = pred_cls[pred_i]
            new_conf[pred_i] = conf[pred_i] 
            iou_return_arr[pred_i] = iou
            detected_boxes += [box_index]
            
    return true_positives, new_pred_cls, new_conf, iou_return_arr

def ap_per_class(tp, conf, pred_cls, target_cls):
    """ Compute the average precision, given the recall and precision curves.
    Source: https://github.com/rafaelpadilla/Object-Detection-Metrics.
    # Arguments
        tp:    True positives (list).
        conf:  Objectness value from 0-1 (list).
        pred_cls: Predicted object classes (list).
        target_cls: True object classes (list).
    # Returns
        The average precision as computed in py-faster-rcnn.
    """

    i = np.argsort(-conf)
    tp, conf, pred_cls = tp[i], conf[i], pred_cls[i]

    # Find unique classes
    unique_classes = np.unique(target_cls)

    # Create Precision-Recall curve and compute AP for each class
    ap, p, r = [], [], []
    for c in tqdm.tqdm(unique_classes, desc="Computing AP"):
        i = pred_cls == c
        # i = pred_cls == c
        n_gt = (target_cls == c).sum()  # Number of ground truth objects
        n_p = i.sum()  # Number of predicted objects

        if n_p == 0 and n_gt == 0:
            continue
        elif n_p == 0 or n_gt == 0:
            ap.append(0)
            r.append(0)
            p.append(0)
        else:
            # Accumulate FPs and TPs
            fpc = (1 - tp[i]).cumsum()
            tpc = (tp[i]).cumsum()

            # Recall
            recall_curve = tpc / (n_gt + 1e-16)
            r.append(recall_curve[-1])

            # Precision
            precision_curve = tpc / (tpc + fpc)
            p.append(precision_curve[-1])

            # AP from recall-precision curve
            ap.append(compute_ap(recall_curve, precision_curve))

    # Compute F1 score (harmonic mean of precision and recall)
    p, r, ap = np.array(p), np.array(r), np.array(ap)
    f1 = 2 * p * r / (p + r + 1e-16)

    return p, r, ap, f1, unique_classes.astype("int32")

def compute_ap(recall, precision):
    """ Compute the average precision, given the recall and precision curves.
    Code originally from https://github.com/rbgirshick/py-faster-rcnn.
    # Arguments
        recall:    The recall curve (list).
        precision: The precision curve (list).
    # Returns
        The average precision as computed in py-faster-rcnn.
    """
    # correct AP calculation
    # first append sentinel values at the end
    mrec = np.concatenate(([0.0], recall, [1.0]))
    mpre = np.concatenate(([0.0], precision, [0.0]))

    # compute the precision envelope
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

    # to calculate area under PR curve, look for points
    # where X axis (recall) changes value
    i = np.where(mrec[1:] != mrec[:-1])[0]

    # and sum (\Delta recall) * prec
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap
    
