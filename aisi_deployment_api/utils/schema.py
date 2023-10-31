import inspect
from fastapi import Form

from typing import List, Optional, Type
from pydantic import BaseModel, Field, DirectoryPath
from pydantic.fields import ModelField

class APIResponse(BaseModel):
    api_success: bool
    message: str

class APISuccessResponse(APIResponse):
    api_success: bool = True
    message: str = "succeeded"

class ErrorDetails(BaseModel):
    status_code: int
    detail: str

class APIFailureResponse(APIResponse):
    api_success: bool = False
    message: str = "failed"
    error_details: ErrorDetails  
    
class Item(BaseModel):
    site_id: str
    tray_id: str

class DeployItem(Item):    
    request_id: str=Field(min_length=1)

class StatusItem(BaseModel):
    request_id: str=Field(min_length=1)

class LogLevel(BaseModel):
    level: str

class ACR_DeployFormItem(BaseModel):
    isGpu: bool
    minMemory: int = Field(gt=0)
    maxMemory: int = Field(gt=0)
    cores:int = Field(gt=0, lt=100)

class AcrImageItem(BaseModel):
    Name: str
    ServicePort: str
    ServiceName: str
    ImageUri: str
    DType: str
    deploymentForm: ACR_DeployFormItem

class ConfigItem(BaseModel):
    connection_string_key_name: str
    Name: str
    output_path: str
    tracking_mode: bool
    workspace_name: str
    project_name: str
    capacity: int = Field(gt=0)
    acrImage: AcrImageItem

class UploadItem(Item):
    history_id: str

class UploadModelItem(BaseModel):
    site_tray_list: List[Item]
    sas_key: str
    local_path: str
    request_id: str
    hyperparameters: dict