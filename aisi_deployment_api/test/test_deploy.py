from distutils.command.config import config
import requests
import json
import time
import pytest

from requests import api
"""
To run this script using pytest:
$ python -m pytest -v test_deploy.py

When adding arguments to python function, pytest treats it as fixtures @pytest.fixture 
"""

reqs = [
    {"tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
    "site_id": "siteid1",
    "request_id": "request1"},
    {"tray_id": "5D2AAB94-3FEA-4703-AA41-E214A6D4817B",
    "site_id": "siteid1",
    "request_id": "request2"},
    {"tray_id": "4E3BB038-B427-4FD0-8E59-78F52CD850D5",
    "site_id": "siteid1",
    "request_id": "request3"},
    {"tray_id": "237B85B8-5319-465B-B8D5-F11FAF8CFBF4",
    "site_id": "siteid1",
    "request_id": "request4"},
]


inference_config_req= {
    "connection_string_key_name": "azureconnectionstringsite1",
    "Name": "AISI INFERENCE API",
    "output_path": "/aisisite1/output/",
    "tracking_mode": False,
    "workspace_name": "AISI_SITE1_WORKSPACE_QA",
    "project_name": "Phase 2",
    "capacity":100,
    "acrImage": {
        'Name': 'AISI INFERENCE API',
        "ServicePort": "80",
        "ServiceName": "AISI-INFERENCE-SERVICE",
        "ImageUri": "mflowacrmflowv1dnav1prod.azurecr.io/aisi_inference_vpcxqa:1.0",
        "DType": "API",
        "deploymentForm": {
            "isGpu": True,
            "minMemory": 80,
            "maxMemory": 80,
            "cores":3
        }
    }
}
deployment_config_req= {
    "connection_string_key_name": "mflowaisitestvpcxqa",
    "Name": "AISI DEPLOYMENT API TEST",
    "output_path": "/aisisite1/output/",
    "tracking_mode": False,
    "workspace_name": "AISI_MLTEST_WORKSPACE",
    "project_name": "Phase 2",
    "capacity":100,
    "acrImage": {
        'Name': 'AISI DEPLOYMENT API TEST',
        "ServicePort": "80",
        "ServiceName": "AISI-DEPLOYMENT-SERVICE",
        "ImageUri": "mflowacrmflowv1dnav1prod.azurecr.io/aisi_inference_testvpcxqa:1.0",
        "DType": "API",
        "deploymentForm": {
            "isGpu": True,
            "minMemory": 80,
            "maxMemory": 80,
            "cores":3
        }
    }
}
# capacity how many trays can be handled by one API.
# means hard deploy
PORT = 9090

@pytest.fixture
def header():
    token='Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik1yNS1BVWliZkJpaTdOZDFqQmViYXhib1hXMCJ9.eyJhdWQiOiIwNzYwZTA2Ni1iNTZkLTQ2ZjQtOGY0Yy1jZmUzOGVmZmNhMGIiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vM2FjOTRiMzMtOTEzNS00ODIxLTk1MDItZWFmZGE2NTkyYTM1L3YyLjAiLCJpYXQiOjE2NDY2Njg2MjYsIm5iZiI6MTY0NjY2ODYyNiwiZXhwIjoxNjQ2NjcyNTI2LCJhaW8iOiJBVlFBcS84VEFBQUFOMnVpODlqS2tGYTBwbEFsT0dBaytRd1dGUzR1MmU4emNuVjhWZ3BnOVVsTGxvRURGdE8rQmJVVmpvMmFDaWVseVZ2RXZCT2JRSjl5alYzZUxYZUEzZjcrWEpWdFQxVWExNDc4VDRFUXBwWT0iLCJuYW1lIjoiU2FwdXRybywgTGluZ2dpaCBbSkpDVVMgTk9OLUpcdTAwMjZKXSIsIm5vbmNlIjoiNWM5ZWEzMjQtMTczMS00NTVlLTg5MjMtYjY2MDVmMzc5NWRhIiwib2lkIjoiMTY3MmM0MTYtMWFmMi00MTU4LWJmN2UtOGRhODBiODlhMTM4IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiTFNhcHV0cm9AaXRzLmpuai5jb20iLCJyaCI6IjAuQVFRQU0wdkpPaldSSVVpVkF1cjlwbGtxTldiZ1lBZHR0ZlJHajB6UDQ0N195Z3NFQUkwLiIsInJvbGVzIjpbIlVzZXIiXSwic3ViIjoiaGhYQllBYTV3eEhPZ19wZ2p6eEJZZXFqaUxkaDdRYklQMWFxWEhmZThVZyIsInRpZCI6IjNhYzk0YjMzLTkxMzUtNDgyMS05NTAyLWVhZmRhNjU5MmEzNSIsInV0aSI6Ik5mNFY1a25SQUVDSVJIUFF5UXFpQUEiLCJ2ZXIiOiIyLjAifQ.foTic3AmESAefCcnwDNQuzVmicWfuidlFjNP_HJfia09BRJOz7gPQjssaAdvzzT8nTlz6O0C5DHkwl3PX_Zm2tziJt9G5o1Oeb5Wc2tF0Ri6qqI72VMz8HIkOYaVeUYH-Ch5KJmL38z2RHY1GUimwqdZHIcfPQilxKXA3gnYg6ZlYS52aCA7TNfnLOWiGjkeILJ8i0zbx-U5SHmnMdfaXfd9IaqJrSGONud0ZVcjQ6PhB6kBaJ0HsLLE2FNnu2ybKIb3SFsn93ZMnPLcxofgjzlqhkasTRJVtrIeWpHnHMUJEXUcBm0ucwBgy7p7Mp2KAJdsKUfx2xjPu-zyCvPBkg'
    HEADER = {
        'X-Api-Key': '0337a9de-9340-4ee3-8d20-86fbc75b0c8e',
        'authorization': token
        }
    return HEADER

@pytest.fixture
def config_req():
    return inference_config_req

def set_config_default(config_req: dict, header: dict):
    url = f"http://0.0.0.0:{PORT}/set_config_default"
    response = requests.post(url, headers=header, json=config_req)
    return response

def get_config(header: dict):
    url = f"http://0.0.0.0:{PORT}/get_config"
    response = requests.get(url, headers=header)
    return response

def get_settings_info():
    url = f"http://0.0.0.0:{PORT}/settings_info"
    response = requests.get(url)
    return response

# def test_start_deploy():
#     url = f"http://0.0.0.0:{PORT}/start_deploy"
#     response = requests.post(url, headers=HEADER, json=reqs[1])
#     return response

# def test_get_status():
#     url = f"http://0.0.0.0:{PORT}/get_status"
#     response = requests.get(url, headers=HEADER, json=reqs[0])
#     return response

# def test_algos():
#     url = "https://mflow.jnj.com/gw/management/api/algos"
#     response = requests.get(url, headers=HEADER)
#     return response


# def deploy_mflow():
#     #should be run on AWS workspace
#     base_url = "https://mflowapi.jnj.com/mfbbefbf6bc094564b5074bd400c472f1m/config_all"

#     INFERENCE_HEADER = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}
#     response = requests.post(f"{base_url}", headers=INFERENCE_HEADER, json={
#         "output_path": config_req['output_path'],
#         "tracking_mode": config_req['tracking_mode'],
#         "site_tray_comb": [
#             {
#                 "siteId": reqs[1]['site_id'],
#                 "trayId": reqs[1]['tray_id']
#             }
#         ]
#     })

# def setup_certifi():
#     import certifi
#     cafile = certifi.where()
#     with open('cert.cer', 'rb') as infile:
#         customca = infile.read()
#     with open(cafile, 'ab') as outfile:
#         outfile.write(customca)

# Function based
def test_set_config_default(config_req: dict, header: dict):
    response = set_config_default(config_req=config_req, header=header)
    assert response.status_code == 200
    assert response.json() == {'message': 'All configurations were properly set'} 

def test_get_settings_info():
    """
    set_env_config(env_val) gets the VPCX_QA, which finds VPCX_QA.json
    based on the return of the Settings in the main.py, it should return the message accordingly
    """
    response = get_settings_info()
    assert response.status_code == 200
    message = {'REQ_TABLE': 'SipDeployApiRequest', 'DB_TABLE': 'SipDeployApi', 'MFLOW_HOST': 'https://mflow.jnj.com/gw/management/api/'}
    assert response.json() == message

# SCENARIO based
def test_scenario_set_get_config(config_req: dict, header: dict):
    """
    Using inference_config_req dict as config_req,
    1. set the config_req by hitting the set_config_default API in main.py
    2. get the config by hitting the get_config API in main.py
    """
    response = set_config_default(config_req=config_req, header=header)
    assert response.status_code == 200
    assert response.json() == {'message': 'All configurations were properly set'} 

    response = get_config(header=header)
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {'message': {'connection_string_key_name': 'azureconnectionstringsite1', 'Name': 'AISI INFERENCE API', 'output_path': '/aisisite1/output/', 'tracking_mode': False, 'workspace_name': 'AISI_SITE1_WORKSPACE_QA', 'project_name': 'Phase 2', 'capacity': 100, 'acrImage': {'Name': 'AISI INFERENCE API', 'ServicePort': '80', 'ServiceName': 'AISI-INFERENCE-SERVICE', 'ImageUri': 'mflowacrmflowv1dnav1prod.azurecr.io/aisi_inference_vpcxqa:1.0', 'DType': 'API', 'deploymentForm': {'isGpu': True, 'minMemory': 80, 'maxMemory': 80, 'cores': 3}}}}

# res_get_status = test_get_status()
# print(res_get_status)
# print(res_get_status.json())

# hard deploy == first time deployment
# soft deploy == second or more deployment. The deployed are less than capacity on the URL
# res_start_deploy = test_start_deploy()
# print(res_start_deploy)
# print(res_start_deploy.json())

# res_algos = test_algos()
# print(res_algos)
# print(res_algos.text)


