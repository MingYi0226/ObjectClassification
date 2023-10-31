"""
Created by Suchitra Ganapathi
This API is used for training the model
"""

import json
import threading
import sys
from typing import List
import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

import aisi_model as model
from utils.ilogger import logger


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

@app.post('/training')
async def training(request: Request, response: Response):
    '''
    Training api
    '''
    try:
        function_name = "aisi_api.training"
        logger.info(f"{function_name} - API invoked")
        if not request.json:
            response.status_code = 400
            logger.error(f"{function_name} - json not sent")
            return {"message": "json not sent"}

        json_content = await request.json()
        if isinstance(json_content, str):
            json_content = json.loads(json_content)
        logger.debug(f"{function_name} - input params: {json_content}")
        aisi = model.AISI(json_content, is_vpcx=is_vpcx)
        if not aisi.isValid:
            message = "Something went wrong. Possibly siteid, trayid was not correct. Or files were not found in File share"
            logger.error(f"{function_name} - {message}")
            return {"message": message}

        train_thread = threading.Thread(target=aisi.train)
        train_thread.start()
        message = "Model training started successfully"
        logger.info(f"{function_name} - {message}")
        return {"message": message}
    except Exception as e:
        logger.error(f"{function_name} - {e}")
        response.status_code = 500
        return {"message": "Internal Server Error"}

if __name__ == "__main__":
    is_vpcx = sys.argv[1]
    uvicorn.run("aisi_api:app", host='0.0.0.0', port=80)
