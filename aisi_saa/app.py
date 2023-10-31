from fastapi import FastAPI, HTTPException
from utils.middleware import *
import uvicorn

from utils.common import *
from process import *


app = FastAPI()

default_responses = {
    400: {"model": APIFailureResponse},
    422: {"model": APIFailureResponse}
}

@app.on_event("startup")
async def startup_event():
    #prepare tmp folder
    os.makedirs(os.path.join(os.getcwd(), 'tmp'), exist_ok=True)
    # load table names from env virables
    common.SAA_TABLE = os.getenv("AZURE_TABLE_NAME")
    common.DOWNLOAD_TABLE = os.environ["AZURE_TABLE_DOWNLOAD_NAME"]

    common.INFERENCE_CONN_KEY_NAME = os.getenv("INFERENCE_CONN_KEY_NAME")
    common.INFERENCE_FILESHARE = os.getenv("INFERENCE_FILESHARE")
    # add handlers
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_middleware(AuthenticationMiddleware)


@app.post("/make_annotations", response_model=APISuccessResponse, responses=default_responses)
async def make_annotations(item:AnnotationItem):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")

    if threading.active_count() >= common.config.total_thread + 1:
        msg = "Please try a while later."
    else:
        threading.Thread(target=start_annotations_task, args=(item,)).start()
        msg = "making annotations has started"
    
    response = APISuccessResponse(message=f"{msg}")
    return response


@app.post("/set_config", response_model=APISuccessResponse, responses=default_responses)
async def set_config(config:ConfigItem):
    # set config
    common.config = config
    # create internal tables
    create_azure_table(config.connection_string_key_name)
    # prepare return message
    msg = "connection string name was successfully set"
    logger.info(msg)
    response = APISuccessResponse(message=f"{msg}")
    return response
    


@app.get("/get_config", response_model=APISuccessResponse, responses=default_responses)
def get_config():
    config_str = common.config.connection_string_key_name if common.config else ""
    return APISuccessResponse(message=config_str)


@app.get("/get_annotation_status", responses=default_responses)
async def get_annotation_status(statusItem: StatusItem):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    return get_annotation_status_process(statusItem.request_id)


@app.post('/start_download', response_model=APISuccessResponse, responses=default_responses)
async def start_download(item:DownloadItem):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")

    if threading.active_count() >= common.config.total_thread + 1:
        msg = "Please try a while later."
    else:
        threading.Thread(target=start_download_task, args=(item, )).start()
        msg = "download started"
    return {"message": msg}


@app.get('/get_download_status', responses=default_responses)
async def get_download_status(statusItem: StatusItem):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    return get_download_status_process(statusItem.request_id)


@app.post('/copy_autocompletion_metadata')
async def copy_autocompletion_metadata(item:AutoCompletionData):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")

    return copy_config_base(item)


@app.post('/copy_nms_data', responses=default_responses)
async def copy_nms_data(item:AutoNMSData):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    return copy_config_base(item)

@app.post('/copy_config_data', responses=default_responses)
async def copy_config_data(item:AutoConfigData):
    if not common.config:
        raise HTTPException(status_code=404, detail="Configure was not set. Please call /set_config()")
    return copy_config_base(item)

if __name__ == '__main__':
    env_val = sys.argv[1]
    is_vpcx = sys.argv[2]
    set_env_config(env_val)
    
    uvicorn.run("app:app", host='0.0.0.0', port=80)