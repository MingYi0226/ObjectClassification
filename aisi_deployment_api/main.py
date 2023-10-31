import os
import json
import uvicorn
from utils.ilogger import logger

import threading
from fastapi import FastAPI, Request, HTTPException
from utils.schema import *
from utils.middleware import *
from utils.common import *
from utils.azure_table import *
from process import *

app = FastAPI()

default_responses = {
    400: {"model": APIFailureResponse},
    422: {"model": APIFailureResponse}
}

@app.on_event("startup")
async def startup_event():
    common.REQ_TABLE = os.getenv("AZURE_REQ_TABLE_NAME")
    common.DB_TABLE = os.getenv("AZURE_TABLE_NAME")
    common.COPY_TABLE = os.getenv("AZURE_MODEL_COPY_TABLE_NAME")
    common.MFLOW_HOST = os.getenv("MFLOW_HANDSHAKE_ENDPOINT")
    
    common.INFERENCE_CONN_KEY_NAME = os.getenv("INFERENCE_CONN_KEY_NAME")
    common.INFERENCE_FILESHARE = os.getenv("INFERENCE_FILESHARE")
    
    logger.info(f" startup - {common.REQ_TABLE}  - {common.DB_TABLE}")
    

    # add handlers
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_middleware(AuthenticationMiddleware)
    
'''
    Start Deployment
'''
@app.post("/start_deploy")
async def start_deploy(request: Request, item:DeployItem):
    if not common.key_name:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    
    token = request.headers.get("authorization", "")
    res = start_deploy_task(item, token)
    response = APISuccessResponse(message=res)
    return response

@app.post("/deploy")
async def deploy(request: Request, item:DeployItem):
    if not common.key_name:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    
    res = copy_files(item)
    response = APISuccessResponse(message=res)
    return response


@app.post("/re_deploy", response_model=APISuccessResponse, responses=default_responses)
async def start_redeploy(request: Request):
    if not common.key_name:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    token = request.headers.get("authorization", "")
    threading.Thread(target=start_redeploy_task, args=(token,)).start()
    response = APISuccessResponse(message="redeployment has started")
    return response

@app.post("/copy_local_to_storage", response_model=APISuccessResponse, responses=default_responses)
async def copy_local_to_storage(item:UploadModelItem):
    '''
    This api is to upload offline trained model to azure storage using azcopy.
    Request: site_tray_list: list of [site_id, tray_id]
            sas_key: saa connection string to azure file share.
            local_path: local path where offline train model exists
    '''
    if not common.key_name:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    res = upload_task(item)
    
    response = APISuccessResponse(message=res)
    return response

@app.get("/get_copy_local_to_storage_state", responses=default_responses)
async def get_copy_local_to_storage_state(item: StatusItem):
    if not common.key_name:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    url = ""
    state = ''
    
    table_conn_str = get_connection_string(secret_key=common.key_name)
    if table_conn_str is None:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")

    query = f"RowKey eq '{item.request_id}'"
    rows = list(query_row(table_conn_str, common.COPY_TABLE, query))
    if len(rows) == 0:
        return {
            'status': '',
            'details': ''
        }
    state = rows[0]['status']
    try:
        details = json.loads(rows[0]['details'])
    except:
        details = ''
    
    res =  {
        'status': state,
        'details': details
    }
    logger.debug(f'/get_copy_local_to_storage_state {json.dumps(res)}')
    return res

@app.post("/set_config_default", response_model=APISuccessResponse, responses=default_responses)
async def set_config_default(config:ConfigItem):
    common.set_config(config)
    create_azure_table()
    response = APISuccessResponse(message="All configurations were properly set")
    return response


@app.get("/get_config", responses=default_responses)
async def get_config():
    return common.app_config


@app.get("/get_status", responses=default_responses)
async def get_status(item: DeployItem):
    if not common.key_name:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    url = ""
    state = ''
    
    table_conn_str = get_connection_string(secret_key=common.key_name)
    if table_conn_str is None:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")

    query = f"PartitionKey eq '{item.tray_id}' and RowKey eq '{item.request_id}' and site eq '{item.site_id}'"
    rows = list(query_row(table_conn_str, common.REQ_TABLE, query))
    if len(rows) > 0:
        state = rows[0]['status']
        if state.lower() == 'success':
            query = f"PartitionKey eq '{item.site_id}' and RowKey eq '{item.tray_id}'"
            rows = list(query_row(table_conn_str, common.DB_TABLE, query))
            if len(rows) > 0:
                url = rows[0]['url']
    
    res =  {
        "url": url,
        "state": state
    }
    logger.debug(f'/get_status {json.dumps(res)}')
    return res


if __name__ == "__main__":
    function_name = "main.main"
    env_val = os.environ['ENV_VAL']
    is_vpcx = os.environ['ENV_IS_VPCX']
    logger.info(f"{function_name} - env: {env_val}, is_vpcx: {is_vpcx}")
    set_env_config(env_val)
    install_cert()
    PORT = 80
    uvicorn.run("main:app", host='0.0.0.0', port=PORT)