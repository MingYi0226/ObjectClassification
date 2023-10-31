import os
import json
import datetime
import certifi
from utils.wrapper import func_wrapper


from utils.ilogger import logger

app_config: dict()

auth_key='0337a9de-9340-4ee3-8d20-86fbc75b0c8e'
INFERENCE_HEADER = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}


IN_PROGESS = 'In Progress'
SUCCESS = 'Success'
FAILED = 'Failed'


def get_time(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(fmt)

def get_currenttime():
    return datetime.today().strftime('%Y%m%d%H')

def install_cert():
    cafile = certifi.where()
    with open('cert.cer', 'rb') as infile:
        customca = infile.read()
    with open(cafile, 'ab') as outfile:
        outfile.write(customca)

@func_wrapper()
def set_env_config(env_val, **kwargs):
    file_name = f'{env_val}.json'
    json_data = dict()

    install_cert()
    # read env json 
    with open(file_name, 'r') as f:
        json_data = json.load(f)
    # set os env variables
    for key in json_data:
        os.environ[key] = json_data[key]
        logger.info(f"{kwargs['func_name']} - {key} : {json_data[key]}")

class Common():
    def __init__(self):
        self.REQ_TABLE = ""
        self.DB_TABLE = ""
        self.COPY_TABLE = ""
        self.MFLOW_HOST = ""
        self.INFERENCE_CONN_KEY_NAME = ""
        self.INFERENCE_FILESHARE = ""
        # self.MODEL_HISTORY_TABLE = ""
        self.app_config = None
        self.field_names = ['release_version', 'algo_version', 'code_version', 'date_time', 'is_current', 'hyper_params']

    def set_config(self, data):
        self.app_config = data

    @property
    def config(self):
        return self.app_config

    @property
    def key_name(self):
        return self.app_config.connection_string_key_name if self.app_config else ''
    
    @property
    def capacity(self):
        return self.app_config.capacity if self.app_config else 0

    @property
    def output_path(self):
        return self.app_config.output_path if self.app_config else ''

common = Common()
