import inspect
from fastapi import Form

from typing import List, Optional, Type
from pydantic import BaseModel, Field, DirectoryPath
from pydantic.fields import ModelField

def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField  # type: ignore

        new_parameters.append(
             inspect.Parameter(
                 model_field.alias,
                 inspect.Parameter.POSITIONAL_ONLY,
                 default=Form(...) if not model_field.required else Form(model_field.default),
                 annotation=model_field.outer_type_,
             )
         )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, 'as_form', as_form_func)
    return cls

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

class LogLevel(BaseModel):
    level: str

class ConfigItem(BaseModel):
    connection_string_key_name: str
    file_share_path: str
    total_thread: int = Field(gt=0)


class StatusItem(BaseModel):
    request_id: str


class AnnotationItem(BaseModel):
    path_name: str
    tray_id: str
    site_id: str
    sas_key: str
    request_id: str


class TrayItem(BaseModel):
    tray_id: str
    site_id: str


class DownloadItem(TrayItem):
    annotation_path_name: str
    image_path_name: str
    sas_key: str
    request_id: str


class MetaItem(BaseModel):
    component_id: str
    auto_type: str
    sub_type: str
    confidence_threshold: Optional[int] = -1

class CompletionConfig(BaseModel):
    nms: Optional[float]
    components: List[MetaItem]

class AutoNMSData(TrayItem):
    nms: float

class AutoCompletionData(TrayItem):
    request_id: str
    components: List[MetaItem]

class AutoConfigData(TrayItem):
    config: CompletionConfig