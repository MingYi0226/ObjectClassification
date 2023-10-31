from azure.storage.blob import ContainerClient
import cv2
import numpy as np
import json
from utils.ilogger import logger

def blob_list(sas_key, path, extenstion):
    function_name = "blob_list"
    res = []
    try:
        container_client = ContainerClient.from_container_url(sas_key)
        blob_list = container_client.list_blobs(name_starts_with=path)
        res = [blob.name for blob in blob_list if extenstion in blob.name]
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def get_blob(sas_key, path):
    function_name = "get_blob"
    res = None
    try:
        container_client = ContainerClient.from_container_url(sas_key)
        res = container_client.get_blob_client(path)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def json_download(sas_key, path):
    res = None
    blob = get_blob(sas_key, path)
    if blob is not None:
        res = json.loads(blob.download_blob().readall())
    return res

def image_download(sas_key, path):
    img = None
    blob = get_blob(sas_key, path)
    if blob is not None:
        x = np.fromstring(blob.download_blob().readall(), dtype='uint8')
        img = cv2.imdecode(x, cv2.IMREAD_UNCHANGED)
    return img


def upload_json(sas_key, path, data):
    function_name = "upload_json"
    try:
        blob = get_blob(sas_key, path)
        if blob is not None:
            blob.upload_blob(data, overwrite=True)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")