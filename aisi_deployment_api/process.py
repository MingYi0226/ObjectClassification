from ensurepip import version
import requests
import uuid
from utils.ilogger import logger
from utils.common import *
from utils.wrapper import *
from utils.azure_table import *
from utils.file_share import *
from utils.schema import *
import os
import time
from subprocess import Popen, PIPE
import threading
from io import StringIO
import shutil
import csv, json


'''
    Get Deployment Status
'''
def get_deployment_status(host, deploymentId, token):
    response = requests.get(
        f"{host}deployment/{deploymentId}/deploystatus", 
        headers={'authorization': f"{token}"},
        verify=False
    )
    # response = requests.get(
    #     f"{host}deploystatus"
    # )
    return response

'''
    Get Deployment URL
'''
def get_deployment_url(host, deploymentId, token):
    response = requests.get(
        f"{host}deployment/{deploymentId}/url", 
        headers={'authorization': f"{token}"},
        verify=False
    )
    # response = requests.get(
    #     f"{host}url"
    # )
    return response


@func_wrapper()
def trigger_self_deploy(host, app_config:ConfigItem, token, url='', **kwargs):

    body = {
        'Name': app_config.Name, 
        'acrImage': app_config.acrImage.dict()
    }
    body['acrImage']['deploymentForm']['isRedeploy'] = True if url else False
    if not url:
        url = 'm'+str(uuid.uuid4()).replace('-', '')+'m'
    body['acrImage']['deploymentForm']['deployEndpoint'] = url
    workspacename = app_config.workspace_name
    projectname = app_config.project_name
    url = f"{host}deployment/{workspacename}/{projectname}"
    response = requests.post(
        url, 
        headers={'authorization': f"{token}"}, 
        json=body, 
        verify=False)
    # response = requests.get(host+"deploy")
    return response
    
@func_wrapper()
def start_hard_deploy(table_conn_str, site_tray_list, token, url='', **kwargs): # ,test_index=0, test_url=''):
    func_name = kwargs['func_name']
    
    response = trigger_self_deploy(common.MFLOW_HOST, common.config, token, url)
    if response.status_code != 200:
        raise Exception(f'The deployment failed: {response}')
    
    # check if deployment has initialized
    res = json.loads(response.text)
    deploymentInitiated = res['deploymentInitiated']
    deploymentId = res['deploymentId']

    # if not raise error
    if deploymentInitiated != True:
        logger.error("The deployment has not initialized")
        raise Exception('The deployment has not initialized')
    
    # wait for 30 min
    start_time = time.time()

    is_deployed = False
    while(True):
        # get deployment status
        response = get_deployment_status(common.MFLOW_HOST, deploymentId, token)
        if response.text=='Failed' or response.status_code != 200:
            raise Exception(f"The deployment failed: {response}")                   
        elif response.text == 'Deployed':
            is_deployed = True
            break

        logger.info(f"Deployment Status: {response.text}")
        end_time = time.time()

        # wait for 30min
        if (end_time-start_time) > 60*30:
            break

        # try for each 10 sec
        time.sleep(10)

    # if failed to deploy
    if not is_deployed:
        logger.error(f"{func_name} - Waiting deployed status timeout")
        raise Exception("Waiting deployed status timeout")
    logger.info(f'{func_name} - deploymentId: {deploymentId}')

    # get new url
    response = get_deployment_url(common.MFLOW_HOST, deploymentId, token)
    if response.status_code != 200:
        logger.error(f"{func_name} - get_deployment_url response: {response}")
        raise Exception(f"Can not get deployment Url: {response}")

    base_url = response.text
    logger.debug(f'{func_name} - base_url: {base_url}')

    # call config_all
    start_time = time.time()
    is_config_set = False
    while True:
        response = requests.post(f"{base_url}config_all", headers=INFERENCE_HEADER, json={
            "output_path": common.config.output_path,
            "tracking_mode": common.config.tracking_mode,
            "connection_string": common.key_name, 
            "site_tray_comb": site_tray_list
        })
        logger.info(f'{func_name} - config_all response: {response.text}')
        if response.status_code == 200:
            is_config_set = True
            break

        # wait for 1 min
        time.sleep(60)

        end_time = time.time()

        # wait for 30min
        if (end_time-start_time) > 60*30:
            break

    if not is_config_set:
        logger.error(f'{func_name} - Failed to call config_all()')
        raise Exception(f"Failed to call config_all()")

    if not url:
        # insert new URL to table
        db_entity = {
            'PartitionKey': site_tray_list[0]['siteId'],
            'RowKey': site_tray_list[0]['trayId'],
            'url': base_url,
            'created_time': get_time(),
            'updated_time': get_time(),
            'status': 'Normal'
        }
        insert_row(table_conn_str, common.DB_TABLE, db_entity)
    else:
        update_table_status(table_conn_str, site_tray_list, base_url, 'Redeployed')
    return base_url


@func_wrapper()
def start_soft_deploy_add(table_conn_str, url, tray_id, site_id, **kwargs):
    # Prepare entity
    db_entity = {
        'PartitionKey': site_id,
        'RowKey': tray_id,
        'url': url,
        'created_time': get_time(),
        'updated_time': get_time(),
        'status': 'Normal'
    }
    insert_row(table_conn_str, common.DB_TABLE, db_entity)

    # Prepare site/tray list
    data = []
    query = f"url eq '{url}'"
    rows = list(query_row(table_conn_str, common.DB_TABLE, query))
    for row in rows:
        data.append(
            {
                "siteId": row['PartitionKey'],
                "trayId": row['RowKey']
            }
        )
    # Call MFlow api
    req = requests.post(f"{url}set_site_tray_id", json=data, headers=INFERENCE_HEADER)
    logger.debug(f'{kwargs["func_name"]} - {url}set_site_tray_id: {req.text}')
    return True


@func_wrapper()
def start_soft_deploy_update(table_conn_str, url, tray_id, site_id, **kwargs):
    # For update, "created_time" should get from the previous entry 
    query = f"PartitionKey eq '{site_id}' and RowKey eq '{tray_id}' and url eq '{url}'"
    row = list(query_row(table_conn_str, common.DB_TABLE, query))[0]
    previous_created_time = row.get('created_time')
    db_entity = {
        'PartitionKey': site_id,
        'RowKey': tray_id,
        'url': url,
        'created_time': previous_created_time,
        'updated_time': get_time(),
        'status': 'Refreshed'
    }
    # Update entity
    update_row(table_conn_str, common.DB_TABLE, db_entity)
    
    # Call MFlow api
    site_tray_comb = [
        {
            "siteId": site_id,
            "trayId": tray_id
        }
    ]
    req = requests.post(f"{url}refresh_model", json=site_tray_comb, headers=INFERENCE_HEADER)
    logger.debug(f'{kwargs["func_name"]} - {url}refresh_model: {req.text}')
    return True


def start_deploy_task(item, token):
    if threading.active_count() > 2:
        return f"Please try again a while later."

    request_id = item.request_id

    # get maximum tray numbers per each URL
    max_tray = common.capacity
    if max_tray <= 0:
        return 'Capacity is invalid'
    
    table_conn_str = get_connection_string(secret_key=common.key_name)
    query = f"RowKey eq '{request_id}'"

    if len(list(query_row(table_conn_str, common.REQ_TABLE, query))) > 0:
        return 'This request id exists already. Please use a new one'

    threading.Thread(target=start_deploy_thread, args=(item, token,)).start()
    return "deployment has started"

@func_wrapper()
def start_deploy_thread(item, token, **kwargs):
    res = ''
    # parse input param
    tray_id = item.tray_id
    site_id = item.site_id
    request_id = item.request_id

    # prepare entities
    req_entity = {
        'PartitionKey': tray_id,
        'RowKey': request_id,
        'site': site_id,
        'status': IN_PROGESS
    }

    table_conn_str = get_connection_string(secret_key=common.key_name)

    # update request table
    insert_row(table_conn_str, common.REQ_TABLE, req_entity)

    # try to get url from database
    query = f"RowKey eq '{tray_id}' and PartitionKey eq '{site_id}'"
    rows = list(query_row(table_conn_str, common.DB_TABLE, query))

    if len(rows) == 0:
        # check if non-full url is exist
        entire_rows = list(query_row(table_conn_str, common.DB_TABLE))
        
        # get usable URLs
        sites = {}
        for row in entire_rows:
            _url = row['url']
            if _url not in sites:
                sites[_url] = 0
            sites[_url] += 1
        rows = [_key for _key in sites.keys() if sites[_key] < common.capacity]

        if len(rows) == 0:
            # Hard deploy
            site_tray_list = [
                {
                    "siteId": site_id,
                    "trayId": tray_id
                }
            ]
            res = start_hard_deploy(table_conn_str, site_tray_list, token)
        else:
            # Soft deploy 1(Add new url)
            res = start_soft_deploy_add(table_conn_str, rows[0], tray_id, site_id)
    else:
        # Soft deploy 2(Exist)
        res = start_soft_deploy_update(table_conn_str, rows[0]['url'], tray_id, site_id)

    # update status
    str_status = SUCCESS if res else FAILED
    req_entity['status'] = str_status
    update_row(table_conn_str, common.REQ_TABLE, req_entity)


def update_table_status(table_conn_str, site_tray_list, base_url, str_status='Normal'):
    for site_tray in site_tray_list:
        query = f"PartitionKey eq '{site_tray['siteId']}' and RowKey eq '{site_tray['trayId']}' and url eq '{base_url}'"
        row = list(query_row(table_conn_str, common.DB_TABLE, query))[0]
        previous_created_time = row.get('created_time')
        db_entity = {
            'PartitionKey': site_tray['siteId'],
            'RowKey': site_tray['trayId'],
            'url': base_url,
            'created_time': previous_created_time,
            'updated_time': get_time(),
            'status': str_status
        }
        update_row(table_conn_str, common.DB_TABLE, db_entity)

@func_wrapper()
def start_redeploy_task(token, **kwargs):
    table_conn_str = get_connection_string(secret_key=common.key_name)
    urls = get_urls_from_table(common.DB_TABLE, table_conn_str)
    
    for url in urls:
        site_tray_list = urls[url]
        update_table_status(table_conn_str, site_tray_list, url, 'Redeploying')
        endpoint = url.split('/')[-2]
        try:
            url = start_hard_deploy(table_conn_str, site_tray_list, token, url=endpoint, catch=True)
            if not url:
                raise Exception("hard_deploy failed.")
            # Call MFlow api
            req = requests.post(f"{url}set_site_tray_id", json=site_tray_list, headers=INFERENCE_HEADER)

            logger.debug(f'{kwargs["func_name"]} - {url}set_site_tray_id: {req.text}')
            logger.info(f'{url} successfully redeployed')
            res = 'Redployed'
        except Exception as e:
            res = f'{e}'
            logger.error(f'{url} Redeploy failed: {res}')
        finally:
            update_table_status(table_conn_str, site_tray_list, url, res)

def upload_task(item:UploadModelItem):
    if threading.active_count() > 2:
        return f"Please try again a while later."

    # validate request_id
    table_conn_str = get_connection_string(secret_key=common.key_name)
    query = f"RowKey eq '{item.request_id}'"
    if len(list(query_row(table_conn_str, common.COPY_TABLE, query))) > 0:
        return 'This request id exists already. Please use a new one'

    # validate local credential
    sas_key = item.sas_key
    if len(sas_key.split('?')) < 2:
        return 'local sas_key is invalid'

    # validate local path
    if not item.local_path:
        return 'local path is invalid'

    # validate output path
    if not common.output_path:
        return 'config.output_path is invalid'
        
    threading.Thread(target=start_upload_task, args=(item,)).start()
    return "Copying has started"


@func_wrapper()
def start_upload_task(item:UploadModelItem, **kwargs):
    # load parameters
    tmp = item.sas_key.split('?')
    src_base, src_access = tmp[0], tmp[1]
    
    src_local = item.local_path
    if src_local[-1] == '/':
        src_local = src_local[:-1]

    output_path = common.output_path
    file_share = output_path.split('/')[1]
        
    # get shared access
    conn_str = get_connection_string(secret_key=common.key_name)
    dst_access, acc_name, acc_key = get_SAS_token(file_share, conn_str)

    # prepare entities
    copy_status = []
    req_entity = {
        'PartitionKey': get_time(),
        'RowKey': item.request_id,
        'details': '',
        'status': IN_PROGESS
    }
    for site_tray in item.site_tray_list:
        copy_status.append({
            'site_id': site_tray.site_id,
            'tray_id': site_tray.tray_id,
            'status': 'Pending'
         })

    # update table
    req_entity['details'] = json.dumps(copy_status)
    insert_row(conn_str, common.COPY_TABLE, req_entity)

    for i, site_tray in enumerate(item.site_tray_list):
        site_id = site_tray.site_id
        tray_id = site_tray.tray_id
        copy_status[i]['status'] = IN_PROGESS
        tray_status = SUCCESS

        # temporary path
        tmp_path = f'./tmp/{site_id}/{tray_id}'
        try:
            # confirms this tray has deployed
            query = f"PartitionKey eq '{site_id}' and RowKey eq '{tray_id}'"
            row = list(query_row(conn_str, common.DB_TABLE, query))
            if len(row) == 0:
                raise Exception('Not deployed yet')

            # copy local to tmp
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)
            os.makedirs(tmp_path, exist_ok=True)
            src_path = f'{src_base}/{src_local}/{site_id}/{tray_id}/current'
            
            if not file_copy(f'{src_path}/*?{src_access}', tmp_path):
                raise Exception("Can not copy from local")

            # validate copying files
            if not validate_model(tray_id, tmp_path):
                raise Exception("Can not copy from local")

            # download train_tracking.csv
            csv_name = 'train_tracking.csv'
            dst_path = f'https://{acc_name}.file.core.windows.net{output_path}{site_id}/{tray_id}/{csv_name}'
            csv_path = f'{tmp_path}/{csv_name}'
            is_exist = file_copy(f'{dst_path}?{dst_access}', csv_path)

            if not is_exist:

                last_modified = GetProperties(acc_name, acc_key, file_share, f'output/{site_id}/{tray_id}', f'{tray_id}.pkl').properties.last_modified
                if not last_modified:
                    raise Exception("Can not read last_modified datetime")
                last_timestamp = last_modified.strftime("%Y%m%d%H%M%S")
                print(last_timestamp)
                

                init_version = f"0_{last_timestamp}"
                init_history_path = f'history/{init_version}'

                # copy current to history/0_datetime
                dst_path = f'https://{acc_name}.file.core.windows.net{output_path}{site_id}/{tray_id}'
                src_url = f'{dst_path}/*?{dst_access}'
                dst_url = f'{dst_path}/{init_history_path}/?{dst_access}'
                if not file_copy(src_url, dst_url):
                    raise Exception(f"Can not copy current to {init_history_path}")

                src_url = f'{dst_path}/*?{dst_access}'
                if not model_remove(src_url, exclude_dir='history'):
                    raise Exception(f"Can not remove previous models")

                # upload version.json
                version_json = {
                    'algo_version': 0,
                    'code_version': 0
                }
                version_path = f'{tmp_path}/init_version.json'
                with open(version_path, 'w') as f:
                    json.dump(version_json, f)
                src_url = version_path
                dst_url = f'{dst_path}/{init_history_path}/version.json?{dst_access}'
                if not file_copy(src_url, dst_url):
                    raise Exception(f"Can not copy version.json to {init_history_path}")
                
                # create train.csv
                create_trackign_csv(csv_path, 0, last_timestamp)

            # copy local file structure as current
            dst_path = f'https://{acc_name}.file.core.windows.net{output_path}{site_id}/{tray_id}/current'
            if not file_copy(f'{src_path}/*?{src_access}', f'{dst_path}/?{dst_access}'):
                raise Exception("Can not copy to fileshare/current")
                       
            # update train_tracking.csv
            version_path = os.path.join(tmp_path, 'version.json')
            try:
                with open(version_path, 'r') as f:
                    version_csv = json.load(f)
                if 'algo_version' not in version_csv or 'code_version' not in version_csv:
                    raise Exception("Invalid version.json format")
            except Exception as e:
                raise Exception("Can not parse version.json")
            hist_dir_name = update_tracking_csv(csv_path, item.hyperparameters, version_csv)
            if not hist_dir_name:
                raise Exception("Can not update, it seems like train.csv is empty.")

            # upload train_tracking.csv
            dst_path = f'https://{acc_name}.file.core.windows.net{output_path}{site_id}/{tray_id}'
            if not file_copy(csv_path, f'{dst_path}?{dst_access}'):
                raise Exception("Can not update train_tracking.csv")

            # upload to history
            dst_path = f'https://{acc_name}.file.core.windows.net{output_path}{site_id}/{tray_id}/history/{hist_dir_name}'
            if not file_copy(f'{src_path}/*?{src_access}', f'{dst_path}/?{dst_access}'):
                raise Exception("Can not copy to fileshare/history")

        except Exception as e:
            tray_status = str(e)
            logger.error(f'{site_id}/{tray_id}: {e}')
        finally:
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)
            copy_status[i]['status'] = tray_status
            req_entity['details'] = json.dumps(copy_status)
            update_row(conn_str, common.COPY_TABLE, req_entity)
    req_entity['status'] = "Finished"
    update_row(conn_str, common.COPY_TABLE, req_entity)
   

def validate_model(tray_id, tmp_path):
    model_files = os.listdir(tmp_path)
    test_files = [
         os.path.join(tmp_path, 'metrics.json'),
         os.path.join(tmp_path, 'model.pkl'),
         os.path.join(tmp_path, 'categories.json'),
         os.path.join(tmp_path, 'version.json'),
         os.path.join(tmp_path, 'reference', 'annotations', 'reference_annotation_0.json'),
         os.path.join(tmp_path, 'reference', 'images', 'reference_image_0.jpg')
    ]
    for f in test_files:
        if not os.path.exists(f):
            logger.error(f'{f} does not exist')
            return False
    
    return True

@func_wrapper()
def model_remove(src_url, exclude_dir='backup', **kwargs):
    process = Popen(['./azcopy2', 'rm', src_url, '--recursive', '--exclude-path', exclude_dir], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if not ParseAZResult(stdout.decode('utf-8')):
        raise Exception("Failed to remove model")
    logger.debug(f'Success: remove {src_url}')
    return True

@func_wrapper()
def file_copy(src_url, dst_url, exclude_dir='backup', **kwargs):
    process = Popen(['./azcopy2', 'cp', src_url, dst_url, '--recursive', '--exclude-path', exclude_dir], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    logger.info(f"file copy status - {str(stdout)}")
    if not ParseAZResult(stdout.decode('utf-8')):
        raise Exception("Failed to copy files")
    logger.debug(f'Success: {src_url} => {dst_url}')
    return True

def create_trackign_csv(csv_path, version_name, last_update):
    new_line = {
        'release_version': version_name,
        'algo_version': '0',
        'code_version': '0',
        'date_time': last_update,
        'is_current': True,
        'hyper_params': '',
    }
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=common.field_names)
        writer.writeheader()
        writer.writerow(new_line)

def update_tracking_csv(csv_path, hyper_params, version_csv):
    history = []
    version_list = []
    if not os.path.exists(csv_path):
        return ''

    with open(csv_path, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=common.field_names)
        for i,row in enumerate(reader):
            if i > 0:
                row['is_current'] = False
                version_list.append(int(row['release_version']))
            history.append(row)
    new_version = max(version_list) + 1
    update_time = get_time("%Y%m%d%H%M%S")
    hist_name = f'{new_version}_{update_time}'
    new_line = {
        'release_version': new_version,
        'algo_version': version_csv['algo_version'],
        'code_version': version_csv['code_version'],
        'date_time': update_time,
        'is_current': True,
        'hyper_params': hyper_params,
    }
    history.append(new_line)
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=common.field_names)
        for row in history:
            writer.writerow(row)
    return hist_name    

def get_version_data(from_conn, file_share, site_id, tray_id):
    function_name = 'get_version_data'
    version_file_path = f"output/{site_id}/{tray_id}/train_tracking.csv"
    # logger.info(f'version file info - {version_file_path}, -  {from_conn}, - {file_share}')

    try:
        file_client = ShareFileClient.from_connection_string(conn_str=from_conn, 
                    share_name=file_share, 
                    file_path=version_file_path)

        logger.info(f'version file path - {version_file_path}, -  {from_conn}, - {file_share}')

        data = file_client.download_file()
        csvreader = csv.reader(StringIO(data.content_as_bytes().decode('utf-8')))
        res_row = []
        for i, row in enumerate(csvreader):
            if i==0:
                cols = row
            res_row.append(row[4])
            if row[4]=='True':
                res_row = row
        if res_row:
            res_row = dict(zip(cols, res_row))
        else:
            res_row = {}
        api_version = "api_v" + res_row['algo_version'] if 'algo_version' in res_row else 'api_v0'
        model_version = "v" + res_row['release_version'] if'release_version' in res_row else 'v0'
        return api_version, model_version
    except Exception as e:
        logger.error(f'Loading version data {version_file_path} - {site_id}/{tray_id}: {e}')
        return f"Error - from {function_name} failed to copy data {e} ,"

def copy_files(item):
    try:
        # parse input param
        tray_id = item.tray_id
        site_id = item.site_id
        
        output_path = common.output_path
        file_share = output_path.split('/')[1]
        
        # get shared access sas token and construct source url
        from_conn = get_connection_string(secret_key=common.key_name)
        if not from_conn:
            logger.error(f'could not get connection string for - {common.key_name} - {from_conn} - {file_share}')
            
            # return json.dumps({'status':f'could not get connection string for - {common.key_name} - {from_conn} - {file_share}'})
        
        src_access, src_acc_name, _ = get_SAS_token(file_share, from_conn)
        src_path = f'https://{src_acc_name}.file.core.windows.net{output_path}{site_id}/{tray_id}/current'
        
        logger.info(f' Tracing the conection string key and fileshare pint - {common.INFERENCE_CONN_KEY_NAME} - {common.INFERENCE_FILESHARE} ')
        
        # et shared access sas token and construct destination url
        to_conn = get_connection_string(secret_key= common.INFERENCE_CONN_KEY_NAME) 
        if not to_conn:
            logger.error(f' could not get connection string for - {common.INFERENCE_CONN_KEY_NAME}- {to_conn} - {common.INFERENCE_FILESHARE}')
            raise Exception(f'could not get connection string for - {common.key_name} - {from_conn} - {file_share}')
        
        dst_access, dst_acc_name, _ = get_SAS_token(common.INFERENCE_FILESHARE, to_conn)
        version_file_path = f"output/{site_id}/{tray_id}/train_tracking.csv"
        logger.info(f'version file path - {version_file_path}')
        
        try:
            api_version, model_version = get_version_data(from_conn, file_share, site_id, tray_id)
        except:
            logger.error(f'Loading version data {version_file_path} - {site_id}/{tray_id}: {e}')
            raise Exception(f'Loading version data {version_file_path} - {site_id}/{tray_id}: {e}')
            
        dst_path = f'https://{dst_acc_name}.file.core.windows.net/{common.INFERENCE_FILESHARE}/model-collection/{site_id}/{tray_id}/{api_version}/{model_version}'
        src_url = f'{src_path}/*?{src_access}'
        dst_url = f'{dst_path}/?{dst_access}'

        if not file_copy(src_url, dst_url):
            raise Exception(f"Can not copy current to aisiinference fileshare {src_url} - {dst_url}")
            
        # to copy config file, which segregated outside
        fol_path = output_path.replace('output', 'config')
        src_path = f'https://{src_acc_name}.file.core.windows.net{fol_path}{site_id}/{tray_id}/config.json'
        dst_path = f'https://{dst_acc_name}.file.core.windows.net/{common.INFERENCE_FILESHARE}/config/{site_id}/{tray_id}/config.json'
        src_url = f'{src_path}?{src_access}'
        dst_url = f'{dst_path}?{dst_access}'
    
        if not file_copy(src_url, dst_url):
            logger.info(f"can not copy config.json to fileshare - {src_url}")

    except Exception as e:
        logger.error(f'{site_id}/{tray_id}: {e}')
        return json.dumps({'status': f"Failed to copy data: Eror - {e}"})
    return_data = {'api_version':api_version,
    'model_version': model_version,
    'status':f"successfully copied {site_id}/{tray_id} data"}
    return json.dumps(return_data)

    