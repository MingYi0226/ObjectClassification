import os
from subprocess import Popen, PIPE
from cv2 import PSNR
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient
from azure.storage.file.sharedaccesssignature import FileSharedAccessSignature
from azure.storage.file.models import SharePermissions
from utils.common import *
from utils.ilogger import logger

def dir_exist(conn_str, file_share, path):
    function_name = "dir_exist"
    bExist = False
    try:
        service = ShareDirectoryClient.from_connection_string(
                conn_str=conn_str,
                share_name=file_share, 
                directory_path=path)
        props = service.get_directory_properties()
        bExist = props['is_directory']
    except Exception as e:
        bExist = False
        logger.error(f"{function_name}: err: {e}")
    return bExist

def del_dir(conn_str, file_share, path):
    function_name = "del_dir"
    try:
        parent_path = os.path.dirname(path)
        file_name = os.path.basename(path)
        serv = ShareDirectoryClient.from_connection_string(
            conn_str=conn_str,
            share_name=file_share, 
            directory_path=parent_path)
        serv.delete_subdirectory(file_name)
    except Exception as e:
        err_msg = f'Remove {path} failed: {e}'
        logger.error(f"{function_name}: remove {path} failed: err: {e}")
        raise Exception(err_msg)

def ParseConnectionString(conn_str):
    json_str = {}
    for key in conn_str.split(';'):
        tmp = key.split('=')
        if len(tmp) < 2:
            continue
        json_str[tmp[0]] = key.replace(f'{tmp[0]}=','')
    return json_str

def get_SAS_token(file_share, conn_str, expire_d=1):
    function_name = "get_SAS_token"
    sas_token = ''
    try:
        # parse connection string
        json_str = ParseConnectionString(conn_str)

        # get account name
        acc_name = json_str['AccountName']

        # get account key
        acc_key = json_str['AccountKey']

        # make permission
        perm = SharePermissions(read=True, write=True, delete=True,list=True)

        # get expire time
        expire_time = datetime.now() + timedelta(days=expire_d)
        
        sig = FileSharedAccessSignature(acc_name, acc_key)
        sas_token = sig.generate_share(share_name=file_share, permission=perm, expiry=expire_time.strftime('%Y-%m-%d'))
        # sas_token = f'https://{acc_name}.file.core.windows.net/{file_share}?{access}'
    except Exception as e:
        err_msg = f'Failed to get SAS token: {e}'
        logger.error(f"{function_name}: err: {e}")
        raise Exception(err_msg)
    return sas_token, acc_name

def az_copy_dir(conn_str, file_share, path_from, path_to):
    function_name = "az_copy_dir"
    res = False
    try:
        # get shared access
        share_access, acc_name = get_SAS_token(file_share, conn_str)

        # src url
        src_url = f'https://{acc_name}.file.core.windows.net/{file_share}/{path_from}/*?{share_access}'

        # dst url
        dst_url = f'https://{acc_name}.file.core.windows.net/{file_share}/{path_to}/?{share_access}'

        process = Popen(['./azcopy2', 'cp', src_url, dst_url, '--recursive'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        res = ParseAZResult(stdout.decode('utf-8'))

    except Exception as e:
        err_msg = (f'az copy failed: {e}')
        logger.error(f"{function_name}: err: {e}")
        raise Exception(err_msg)
    return res

def az_empty_dir(conn_str, file_share, _path):
    function_name = "az_empty_dir"
    res = False
    # get shared access
    share_access, acc_name = get_SAS_token(file_share, conn_str)
    try:
        _url = f'https://{acc_name}.file.core.windows.net/{file_share}/{_path}?{share_access}'
        process = Popen(['./azcopy2', 'rm', _url, '--recursive'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        res = ParseAZResult(stdout.decode('utf-8'))
        
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return res

def mv_dir(conn_str, file_share, path_from, path_to):
    function_name = "mv_dir"
    logger.info(f'Moving {path_from} to {path_to}.....')
    try:
        res = az_empty_dir(conn_str, file_share, path_to)
        logger.info(f'{function_name}: rm {path_to} :{res}')
        res = az_copy_dir(conn_str, file_share, path_from, path_to)
        logger.info(f'{function_name}: cp {path_from} to {path_to} :{res}')
        res = az_empty_dir(conn_str, file_share, path_from)
        logger.info(f'{function_name}: rm {path_from} :{res}')
    except Exception as e:
        logger.error(f"{function_name}: Move from {path_from} to {path_to} failed: {e}")

def az_blob2share(saa_token, conn_str, share_name, blob_ann, blob_img, share_ann, share_img):
    function_name = "az_blob2share"
    res_ann = False
    res_img = False
    try:
        blob_list = saa_token.split('?')
        blob_ann_url = f'{blob_list[0]}/{blob_ann}/*?{blob_list[1]}'

        share_access, acc_name = get_SAS_token(share_name, conn_str)
        share_ann_url = f'https://{acc_name}.file.core.windows.net/{share_name}/{share_ann}?{share_access}'
        
        process = Popen(['./azcopy2', 'cp', blob_ann_url, share_ann_url, '--recursive'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        res_ann = ParseAZResult(stdout.decode('utf-8'))

        blob_img_url = f'{blob_list[0]}/{blob_img}/*?{blob_list[1]}'

        share_access, acc_name = get_SAS_token(share_name, conn_str)
        share_img_url = f'https://{acc_name}.file.core.windows.net/{share_name}/{share_img}?{share_access}'

        process = Popen(['./azcopy2', 'cp', blob_img_url, share_img_url, '--recursive'], stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        res_img = ParseAZResult(stdout.decode('utf-8'))
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    logger.info(f'{function_name}: cp {blob_ann_url} to {share_ann_url}: {res_ann}')
    logger.info(f'{function_name}: cp {blob_img_url} to {share_img_url}: {res_img}')
    return res_ann and res_img

def ParseAZResult(txt):
    function_name = "ParseAZResult"
    rs = dict()
    bSuccess = False
    try:
        lines = txt.split('\n')
        for line in lines:
            tmp = line.split(':')
            if len(tmp) == 2:
                rs[tmp[0]] = tmp[1].strip()
        res = rs['Final Job Status'] == 'Completed'
        nFiles = int(rs['Number of File Transfers'])
        nFolders = int(rs['Number of Folder Property Transfers'])
        nTotal = int(rs['Total Number of Transfers'])
        bSuccess = res and (nTotal==(nFiles+nFolders)) and (nTotal > 0)
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
    return bSuccess

def back_up(base_dir, key_word, conn_str, share_name):
    try:
        path_from = f"{base_dir}/{key_word}"
        path_to = f"{base_dir}/{key_word}_bak"

        bExist = dir_exist(conn_str, share_name, path_from)
        if bExist:
            mv_dir(conn_str, share_name, path_from, path_to)
        return path_from, path_to
    except Exception as e:
        return '', ''