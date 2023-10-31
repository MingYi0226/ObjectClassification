from utils.common import *
from utils.file_share import *


def set_env_config(env_val):
    function_name ="set_env_config"
    file_name = f'{env_val}.json'
    json_data = dict()
    try:
        with open(file_name, 'r') as f:
            json_data = json.load(f)
        for key in json_data:
            os.environ[key] = json_data[key]
        logger.info(f"{function_name}: done")
    except Exception as e:
        logger.error(f'{function_name}: Failed to set config: {e}')


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_currenttime():
    return datetime.today().strftime('%Y%m%d%H')


@func_wrapper()
def compare_anchor(sas_key, anchor_list, path_name, filename, anns, **kwargs):
    function_name = "compare_anchor"
    anchor_path = ''
    for _path in anchor_list:
        json_name = re.findall(r'[^\/]+(?=\.)', _path)[0]
        if json_name == filename:
            anchor_path = _path
            break
    if not anchor_path:
        return
    anchor_json = json_download(sas_key, anchor_path)
    if anchor_json is None:
        return
    anchor_anns = anchor_json['components']
    iou_arr = []
    for pre, act in zip(anns, anchor_anns):
        iou = 0
        # determine the coordinates of the intersection rectangle
        x_left = max(pre['xMin'], act['xMin'])
        y_top = max(pre['yMin'], act['yMin'])
        x_right = min(pre['xMax'], act['xMax'])
        y_bottom = min(pre['yMax'], act['yMax'])
        if x_right < x_left or y_bottom < y_top:
            iou_arr.append(iou)
            continue
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        # compute the area of both AABBs
        bb1_area = (pre['xMax'] - pre['xMin']) * (pre['yMax'] - pre['yMin'])
        bb2_area = (act['xMax'] - act['xMin']) * (act['yMax'] - act['yMin'])
        # compute iou
        iou = intersection_area / float(bb1_area + bb2_area - intersection_area + 1e-16)
        iou_arr.append(iou)
    mean_iou = np.mean(iou_arr)
    blob_path = f"{path_name}/saa/anchor_annotation_comparison/{filename}.json"
    upload_json(sas_key, blob_path, json.dumps({
        'anchor_deviation': mean_iou
    }))
    logger.info(f'{function_name} compared json file save to {blob_path}')


@func_wrapper()
def anticipate_annotations(sift, prev_img, img, annotations, **kwargs):
    res = copy.deepcopy(annotations)

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(prev_img, None)
    kp2, des2 = sift.detectAndCompute(img, None)
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < MIN_DIST_THRESHOLD * n.distance:
            good.append(m)
    
    if len(good) > MIN_MATCH_COUNT:
        # get transform matrix
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, RANSAC_REPROJ_THRESHOLD)
        
        height, width, _ = img.shape
        # iterate result
        for i,x in enumerate(res):
            # source annotation
            srcRT = [ x['xMin'], x['yMin'], x['xMax'], x['yMax']]
            
            # get estimated mapping
            pts = np.float32([ [srcRT[0],srcRT[1]],[srcRT[0],srcRT[3]],[srcRT[2],srcRT[3]],[srcRT[2],srcRT[1]] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)

            # get boundary
            pt1 = [(dst[0][0][0]+dst[1][0][0])/2, (dst[0][0][1]+dst[3][0][1])/2]
            pt2 = [(dst[2][0][0]+dst[3][0][0])/2, (dst[1][0][1]+dst[2][0][1])/2]
            
            # prepare result
            res[i]['xMin'] = min(max(0, pt1[0]), width-1)
            res[i]['yMin'] = min(max(0, pt1[1]), height-1)
            res[i]['xMax'] = min(max(0, pt2[0]), width-1)
            res[i]['yMax'] = min(max(0, pt2[1]), height-1)
    return res


@func_wrapper()
def start_annotations_task(item:AnnotationItem, **kwargs):
    function_name = kwargs['func_name']

    # pre process
    if item.path_name[-1] == '/':
        item.path_name = item.path_name[:-1]

    # make entity
    entity = {
        'PartitionKey': get_currenttime(),
        'RowKey': item.request_id,
        'description': '',
        'updated_time': get_time(),
        'start_time': get_time(),
        'finish_time': '',
        'status': IN_PROGESS
    }
    
    # init status
    progress_info = [0, 0, 0]
    try:
        # get azure table connection string
        table_conn_str = get_connection_string(secret_key=common.config.connection_string_key_name)

        # try to get url from database
        query = f"RowKey eq '{item.request_id}'"
        exist_rows = list(query_row(table_conn_str, common.SAA_TABLE, query))
        if len(exist_rows) > 0:
            entity['PartitionKey'] = exist_rows[0].PartitionKey
            raise Exception('This request id exists already. Please use a new one')

        sift = cv2.xfeatures2d.SIFT_create()
    
        # update request table
        insert_row(table_conn_str, common.SAA_TABLE, entity)
        
        # get file list in 'extracted_image'
        filelist = blob_list(item.sas_key, f"{item.path_name}/extracted_image", '.jpg')
        
        # get anchor file list in 'manual_annotation/anchor_annotation
        anchor_list = blob_list(item.sas_key, f"{item.path_name}/manual_annotation/anchor_annotation", '.json')
        
        # load initial annotation file
        init_json = json_download(item.sas_key, f"{item.path_name}/manual_annotation/start.json")
        
        # init progress variable
        progress_info[0] = len(filelist)
        
        if init_json is None:
            raise Exception('/manual_annotation/start.json is not exist')
        
        # update tray_id and site_id
        init_json['tray_id'] = item.tray_id
        init_json['site_id'] = item.site_id
        
        prev_img = None
        prev_json = init_json
        
        for i in range(len(filelist)):
            # get file path
            _name = filelist[i]
            # get filename
            jpg_name = re.findall(r'[^\/]+(?=\.)', _name)[0]
            if i == 0:
                default_tray_name = jpg_name
            # load image
            img = image_download(item.sas_key, _name)

            if img is None:
                if i == 0:
                    raise Exception("Can not read first image.")
                logger.error(f"{function_name}: cannot read {_name}")
                continue
            # update progress
            progress_info[1] = i+1
            # update fileName in json
            prev_json['fileName'] = _name
            
            if i == 0:
                # update progress
                progress_info[2] += 1
            else:
                res = anticipate_annotations(sift, prev_img, img, prev_json['components'], save_param=False, cache=True)
                prev_json['components'] = res
                # update progress
                progress_info[2] += 1
                # compare with anchor json
                compare_anchor(item.sas_key, anchor_list, item.path_name, jpg_name, res, save_param=False)
            prev_img = img.copy()
            
            # write json as blob
            blob_path = f"{item.path_name}/saa/annotations/{jpg_name}.json"
            logger.info(f"{function_name}: {progress_info} -> {blob_path}")
            upload_json(item.sas_key, blob_path, json.dumps(prev_json))
            
            if i % 5 == 0:
                _statics = f"Total: {progress_info[0]}, Current:{progress_info[1]}, Processed:{progress_info[2]}"
                # update request table
                entity['description'] = _statics
                entity['updated_time'] = get_time()
                update_row(table_conn_str, common.SAA_TABLE, entity)

        # update status for error
        entity['status'] = SUCCESS
        entity['description'] = f"Total: {progress_info[0]}, Current:{progress_info[1]}, Processed:{progress_info[2]}"
    except Exception as e:
        logger.error(f'{function_name}: {e}')
        # update status for error
        entity['description'] = f"{e}"
        entity['status'] = FAILED
    finally:
        # update table record
        entity['finish_time'] = get_time()
        update_row(table_conn_str, common.SAA_TABLE, entity)


@func_wrapper()
def get_annotation_status_process(request_id, **kwargs):
    last_update = desc = status = start_time = finish_time = ''
    function_name = kwargs['func_name']
    try:
        table_conn_str = get_connection_string(secret_key=common.config.connection_string_key_name)

        query = f"RowKey eq '{request_id}'"
        rows = list(query_row(table_conn_str, common.SAA_TABLE, query))
        if len(rows) > 0:
            last_update = rows[0].updated_time
            desc = rows[0].description
            status = rows[0].status
            start_time = rows[0].start_time
            finish_time = rows[0].finish_time
        
    except Exception as e:
        desc = f"{function_name} - {e}"
        logger.error(desc)

    return {
        "last_update" : last_update,
        "description" : desc,
        "status": status,
        'start_time': start_time,
        'finish_time': finish_time,
    }

@func_wrapper()
def start_download_task(item:DownloadItem, **kwargs):
    function_name = kwargs['func_name']
    # make entity
    entity = {
        'PartitionKey': get_currenttime(),
        'RowKey': item.request_id,
        'description': '',
        'start_time': get_time(),
        'finish_time': '',
        'status': IN_PROGESS
    }
    
    try:
        # get azure table connection string
        storage_conn_str = get_connection_string(secret_key=common.config.connection_string_key_name)

        input_path = common.config.file_share_path
        # get share name from intput path
        share_name = input_path.split('/')[1]

        query = f"RowKey eq '{item.request_id}'"
        exist_rows = list(query_row(storage_conn_str, common.DOWNLOAD_TABLE, query))
        if len(exist_rows) > 0:
            entity['PartitionKey'] = exist_rows[0].PartitionKey
            raise Exception('This request id exists already. Please use a new one')

        # update request table
        insert_row(storage_conn_str, common.DOWNLOAD_TABLE, entity)  

        # get absoulute path inside file share
        base_path = input_path.replace(f'/{share_name}/', '')
        root_path = f"{base_path}/{item.site_id}/{item.tray_id}"

        # make path for annotations
        ann_path_from, ann_path_to = back_up(root_path, "annotations", storage_conn_str, share_name)
        if len(ann_path_from) == 0 or len(ann_path_to) == 0:
            raise Exception('Failed to backup annotations')

        # make path for images
        img_path_from, img_path_to = back_up(root_path, "images", storage_conn_str, share_name)
        if len(img_path_from) == 0 or len(img_path_to) == 0:
            raise Exception('Failed to backup images')

        # copy annotations to file share
        res = az_blob2share(
            item.sas_key, 
            storage_conn_str, 
            share_name, 
            item.annotation_path_name, 
            item.image_path_name, 
            ann_path_from, 
            img_path_from
        )
        logger.info(f'{function_name}: Blob to Share: {res}')
        if not res:
            raise Exception("Failed to download")
        tmp = az_empty_dir(storage_conn_str, share_name, ann_path_to)
        logger.info(f'{function_name}: rm ann_path_to {ann_path_to}: {tmp}')

        tmp = az_empty_dir(storage_conn_str, share_name, img_path_to)
        logger.info(f'{function_name}: rm img_path_to {img_path_to}: {tmp}')

        entity['description'] = "Success"
        entity['status'] = SUCCESS
    except Exception as e:
        res = False
        entity['description'] = f"{e}"
        entity['status'] = FAILED
        logger.error(str(e))
    finally:
        if not res:
            try:
                if share_name:
                    mv_dir(storage_conn_str, share_name, ann_path_to, ann_path_from)
                    mv_dir(storage_conn_str, share_name, img_path_to, img_path_from)
            except Exception as e:
                logger.error(f"{function_name}: finally - Err: {e}")
        # update status for error
        entity['finish_time'] = get_time()
        update_row(storage_conn_str, common.DOWNLOAD_TABLE, entity)


@func_wrapper()
def get_download_status_process(request_id, **kwargs):
    
    table_conn_str = get_connection_string(secret_key=common.config.connection_string_key_name)
    try:
        query = f"RowKey eq '{request_id}'"
        rows = list(query_row(table_conn_str, common.DOWNLOAD_TABLE, query))

        if len(rows) == 0:
            raise Exception("Record not found")
        desc = rows[0].description
        status = rows[0].status
        start_time = rows[0].start_time
        finish_time = rows[0].finish_time
        training_path = common.config.file_share_path

    except Exception as e:
        logger.error(str(e))
        desc = ''
        status = ''
        start_time = ''
        finish_time = ''
        training_path = ''

    return {
        "description" : desc,
        "status": status,
        'start_time': start_time,
        'finish_time': finish_time,
        'training_path': training_path
    }


def copy_config_base(item):
    site_id = item.site_id
    tray_id = item.tray_id

    table_conn_str = get_connection_string(secret_key=common.config.connection_string_key_name)
    logger.debug("copy_config_data starts")
    res_status = "Failed"
    try:
        
        # get absoulute path inside file share
        share_name = common.config.file_share_path.split('/')[1]
        base_path = os.path.join(f"/{share_name}", "config", site_id, tray_id, 'config.json')
        conn_str = get_connection_string(secret_key=common.config.connection_string_key_name)
        
        share_access, acc_name = get_SAS_token(share_name, conn_str)
        share_ann_url = f'https://{acc_name}.file.core.windows.net{base_path}?{share_access}'
        tmp_path = os.path.join(os.getcwd(), 'tmp', f'{site_id}_{tray_id}.json')

        to_conn = get_connection_string(secret_key= common.INFERENCE_CONN_KEY_NAME) 
        if not to_conn:
            raise Exception(f' could not get connection string for - {common.INFERENCE_CONN_KEY_NAME}- {to_conn} - {common.INFERENCE_FILESHARE}')
        dst_access, dst_acc_name = get_SAS_token(common.INFERENCE_FILESHARE, to_conn)
        dst_path = f'https://{dst_acc_name}.file.core.windows.net/{common.INFERENCE_FILESHARE}/config/{site_id}/{tray_id}/config.json'
        share_ann_second_url = f'{dst_path}?{dst_access}'

        if type(item) != AutoConfigData:
            try:
                # call azcopy to upload
                process = Popen(['./azcopy2', 'cp', share_ann_url, tmp_path], stdout=PIPE, stderr=PIPE)
                logger.debug(f"./azcopy2 cp {tmp_path} {share_ann_url}")
                stdout, _ = process.communicate()
                is_success = ParseAZResult(stdout.decode('utf-8'))
                with open(tmp_path, 'r') as f:
                    out_json = json.load(f)
            except Exception:
                logger.debug('Failed to load existing conf file')
                out_json = {
                    "site_id": site_id,
                    "tray_id": tray_id,
                    "config": {}
                }

            if "config" not in out_json:
                out_json["config"] = {}
            if "components" in out_json:
                out_json["config"]["components"] = out_json["components"]
                del out_json["components"]
            
            if type(item) == AutoNMSData:
                out_json["config"]["nms"] = item.nms
            elif type(item) == AutoCompletionData:
                out_json["config"]["components"] = [meta.dict() for meta in item.components]

        else:
            out_json = {
                "site_id": site_id,
                "tray_id": tray_id,
                "config": {
                    "nms": item.config.nms,
                    "components": [meta.dict() for meta in item.config.components]
                }
            }
        
        # save output as json in tmp
        logger.debug(str(out_json))
        with open(tmp_path, 'w') as f:
            json.dump(out_json, f, indent=4)

        # call azcopy to upload
        process = Popen(['./azcopy2', 'cp', tmp_path, share_ann_url], stdout=PIPE, stderr=PIPE)
        logger.debug(f"./azcopy2 cp {tmp_path} {share_ann_url}")
        stdout, _ = process.communicate()
        is_success = ParseAZResult(stdout.decode('utf-8'))
        if not is_success:
            raise Exception(f"Failed to call azcopy to {share_ann_url}")

        # call azcopy to upload
        process = Popen(['./azcopy2', 'cp', tmp_path, share_ann_second_url], stdout=PIPE, stderr=PIPE)
        logger.debug(f"./azcopy2 cp {tmp_path} {share_ann_second_url}")
        stdout, _ = process.communicate()
        is_success = ParseAZResult(stdout.decode('utf-8'))
        if not is_success:
            raise Exception(f"Failed to call azcopy to {share_ann_second_url}")
        res_status = SUCCESS
    except Exception as e:
        logger.error(str(e))
    finally:
        logger.debug(f'copy_config_base: {res_status}')
        return {"status":  res_status}

