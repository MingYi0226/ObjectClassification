"""
Created by Suchitra Ganapathi
This API is used for inference and scoring
"""

import json
import sys
import asyncio
import uvicorn
from fastapi import FastAPI, Request, Response, File, UploadFile, Form, HTTPException
from typing import List
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
from aisi_score import score
import time
import globals

from ilogger import logger

app = FastAPI()
auth_key = '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
is_vpcx = "yes"

class Config(BaseModel):
    tracking_mode: bool
    output_path: str
    site_tray_comb: List


@app.get("/", status_code=401)
def home():
    return {"message": "Unauthorized Access"} 

@app.post("/", status_code=401)
def home_post():
    return {"message": "Unauthorized Access"}


@app.post('/set_output_path')
def set_output_path(request: Request, response: Response, data: str = Form(...)):
    '''
    set output path 
    '''
    function_name = "set_output_path"
    try:
        auth = request.headers.get("X-Api-Key","")
        
        # provide your auth key value
        if auth != auth_key:
            response.status_code = 201
            logger.error(f"{function_name}: Unauthorized")
            return {"message": "ERROR: Unauthorized"}
        globals.set_output_path(data)

        logger.info(f"{function_name} Output path set: {data}")
        return {"message": "Output path set: "+data}
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
        raise HTTPException(status_code=500, detail=e)
    

@app.post('/set_site_tray_id')
def set_site_tray_id(request: Request, response: Response, site_tray_comb: List):
    '''
    set site id and tray ID combinations
    '''
    function_name = "set_site_tray_id"
    try:
        auth = request.headers.get("X-Api-Key","")
        
        # provide your auth key value
        if auth != auth_key:
            response.status_code = 201
            logger.error(f"{function_name}: Unauthorized")
            return {"message": "ERROR: Unauthorized"}
        globals.set_site_tray_comb_lst(site_tray_comb)

        message = "Site ID and tray ID combinations set."
        logger.info(f"{function_name}: {message}")
        return {"message": message}
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
        raise HTTPException(status_code=500, detail=e)
    

@app.post('/refresh_cache')
def refresh_cache(request: Request, response: Response):
    '''
    Refresh cache 
    '''
    function_name = "refresh_cache"
    try:
        auth = request.headers.get("X-Api-Key","")
        
        # provide your auth key value
        if auth != auth_key:
            response.status_code = 201
            logger.error(f"{function_name}: Unauthorized")
            return {"message": "ERROR: Unauthorized"}

        # provide your api key name
        response = globals.refresh_cache()
        
        logger.info(f"{function_name}: {response}")
        return response
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
        raise HTTPException(status_code=500, detail=e)

@app.post('/set_tracking_mode')
def set_tracking_mode(request: Request, response: Response, tracking_mode: bool = Form(...)):
    function_name = "set_tracking_mode"
    try:
        auth = request.headers.get("X-Api-Key","")
        
        # provide your auth key value
        if auth != auth_key:
            response.status_code = 201
            logger.error(f"{function_name}: Unauthorized")
            return {"message": "ERROR: Unauthorized"}
        
        globals.set_tracking_mode(tracking_mode)

        message = 'set_tracking_mode to '+ str(tracking_mode) 
        logger.info(f"{function_name}: {message}")
        return {"message": message}

    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
        raise HTTPException(status_code=500, detail=e)


@app.post("/config_all")
def config_all(request: Request, response: Response, config: Config):
    '''
    set output path, set tray id, site id and set tracking mode
    '''
    function_name = "config_all"
    try:
        auth = request.headers.get("X-Api-Key","")
        
        # provide your auth key value
        if auth != auth_key:
            response.status_code = 201
            return {"message": "ERROR: Unauthorized"}

        # Set output path    
        globals.set_output_path(config.output_path)
        globals.set_tracking_mode(config.tracking_mode)
        globals.set_site_tray_comb_lst(config.site_tray_comb)
        
        message = "All configurations were succesfully set"
        logger.info(f"{function_name}: {message}")
        return {"message": message}

    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
        raise HTTPException(status_code=500, detail=e)


@app.post('/score_real')
async def score_real(request: Request, response: Response, file: UploadFile = File(...), data: str = Form(...)):
    '''
    Inference api
    '''
    function_name = "score_real"

    # provide your api key name
    logger.info(f"{function_name} api called")
    try:
        start_time = time.time()
        main_start_time=start_time
        auth = request.headers.get("X-Api-Key","")

        # provide your auth key value
        if auth != auth_key:
            response.status_code = 201
            logger.error(f"{function_name}: Unauthorized")
            return {"message": "ERROR: Unauthorized"}

        end_time = time.time()

        logger.info(f"{function_name}: get X-API-Key from header: {end_time-start_time}")

        start_time=time.time()
        img_file= file
        end_time = time.time()
        logger.info(f"{function_name}: get image file: {end_time-start_time}")

        start_time=time.time()
        json_content = json.loads(data)
        end_time = time.time()
        logger.info(f"{function_name}: load json content: {end_time-start_time}")

        start_time=time.time()
        result = await run_in_threadpool(lambda: actual_score(json_content, img_file, is_vpcx))
        end_time = time.time()
        logger.info(f"{function_name}: End to end: {end_time-main_start_time}")
        return result
    
    except Exception as e:
        logger.error(f"{function_name}: err: {e}")
        raise HTTPException(status_code=500, detail=e)


def actual_score(json_content, img_file, is_vpcx):
    result = score(json_content, image_file=img_file, is_vpcx=is_vpcx)
    return result



if __name__ == "__main__":
    is_vpcx = sys.argv[1] 
    uvicorn.run("aisi_api:app", host='0.0.0.0', port=80)
