from datetime import datetime, timedelta
import copy
import sys
import cv2
import re
import os
import json
import threading
import numpy as np
from utils.blob_manage import *
from utils.azure_table import *
from utils.schema import *

from utils.wrapper import func_wrapper
from utils.ilogger import logger

auth_key='896d35d2-a352-4705-b4f5-e8d86724fe52'

IN_PROGESS = 'In Progress'
SUCCESS = 'Success'
FAILED = 'Failed'

# define params
MIN_DIST_THRESHOLD = 0.7
RANSAC_REPROJ_THRESHOLD = 5.0
MIN_MATCH_COUNT = 1
FLANN_INDEX_KDTREE = 1


class Common():
    def __init__(self):
        self.SAA_TABLE = ""
        self.DOWNLOAD_TABLE = ""
        self.config = None

        self.INFERENCE_CONN_KEY_NAME = ""
        self.INFERENCE_FILESHARE = ""


common = Common()