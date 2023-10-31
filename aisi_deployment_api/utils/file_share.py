import os
from subprocess import Popen, PIPE
from utils.common import *
from utils.wrapper import *
from datetime import datetime, timedelta
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient
from azure.storage.file.sharedaccesssignature import FileSharedAccessSignature
from azure.storage.file.models import SharePermissions
from azure.storage.file.fileservice import FileService

@func_wrapper()
def GetProperties(acc_name, acc_key, share_name, dir_name, file_name, **kwargs):
    file_service = FileService(account_name=acc_name, account_key=acc_key)
    return file_service.get_file_properties(share_name, dir_name, file_name)

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
    return sas_token, acc_name, acc_key


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