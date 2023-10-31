import requests
import json
import time

from requests import api

reqs = [
    {
        "tray_id": "E81A1B3A-7EA7-4D03-8A18-8182DA23F350",
        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "496A3534-EBE8-49A6-94A5-490E08329311"
    },
    {
        "tray_id": "7141F261-D5CB-4D55-B510-A6C23A1936F8_Test2",
        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "496A3534-EBE8-49A6-94A5-490E08329312"
    }, # 
    {
        "tray_id": "7141F261-D5CB-4D55-B510-A6C23A1936F8_Test3",
        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "496A3534-EBE8-49A6-94A5-490E08329314"
    },
    {
        "tray_id": "7141F261-D5CB-4D55-B510-A6C23A1936F8_Test4",
        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "496A3534-EBE8-49A6-94A5-490E08329315"
    }
]


config_req= {
    "connection_string_key_name": "azureconnectionstringv2testvpcx",
    "Name": "AISI INFERENCE API Test VPCx",
    "output_path": "/aisiv2testvpcx/output/",
    "tracking_mode": False,
    "workspace_name": "AISI_VPCx_TEST_WS_2.0",
    "project_name": "Phase 2",
    "capacity":2,
    "acrImage": {
        'Name': 'AISI INFERENCE API',
        "ServicePort": "80",
        "ServiceName": "AISI-INFERENCE-SERVICE",
        "ImageUri": "crazraswmflowprod01.azurecr.io/aisi_inference_vpcxtest:2.0",
        "DType": "API",
        "deploymentForm": {
            "isGpu": True,
            "minMemory": 80,
            "maxMemory": 80,
            "cores":3
        }
    }
}
upload_info = {
    'site_tray_list': reqs,
    'sas_key': 'https://aihub01allwus2.file.core.windows.net/aisi?sv=2020-10-02&st=2022-05-18T23%3A23%3A50Z&se=8023-05-19T23%3A23%3A00Z&sr=s&sp=rcwdl&sig=%2FM4LJfwcTD0DdrttzeqfvzBFn9ZScf5O82VRTN3eMg0%3D',
    'local_path': 'phase_2/data/ming/v2/output'
}
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyJ9.eyJhdWQiOiIwNzYwZTA2Ni1iNTZkLTQ2ZjQtOGY0Yy1jZmUzOGVmZmNhMGIiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vM2FjOTRiMzMtOTEzNS00ODIxLTk1MDItZWFmZGE2NTkyYTM1L3YyLjAiLCJpYXQiOjE2NTU0MTcxNDEsIm5iZiI6MTY1NTQxNzE0MSwiZXhwIjoxNjU1NDIxMDQxLCJhaW8iOiJBV1FBbS84VEFBQUEvWDJzaGlUczVjNmpMamV2dWZidXRNcDRraVI0T2RCLzk3aDFwa3BRejRIZlZyRGRYVG42UzFXbXQ4SDJVU1poayt6WmUzdGUyNUlIeGJXNmhSa2VMY0Vxcmk5TTlBWnU1bFdHVXUzZjNrWnNScEF3MHo1RXM5ZG4xaXlxaUVRSyIsIm5hbWUiOiJDdSwgTWluZ3lpIFtKSkNVUyBOT04tSlx1MDAyNkpdIiwibm9uY2UiOiJjY2I0ZjNhMi00MzM5LTRmMGYtYjNlNS1iZjU2YzM2ZWUyYmIiLCJvaWQiOiI1NjRiNzllNi1lMGQyLTRiMDgtYmJjZi00ZWFmYzIxYWY1OTUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJNQ3UzQGl0cy5qbmouY29tIiwicmgiOiIwLkFRUUFNMHZKT2pXUklVaVZBdXI5cGxrcU5XYmdZQWR0dGZSR2owelA0NDdfeWdzRUFMWS4iLCJyb2xlcyI6WyJVc2VyIl0sInN1YiI6IjdQaVppU1VpNWlfc01xWHRwaW85MlVYWXBlUHZaSmRBWUVGOTFUbS12MXciLCJ0aWQiOiIzYWM5NGIzMy05MTM1LTQ4MjEtOTUwMi1lYWZkYTY1OTJhMzUiLCJ1dGkiOiJpSmt3LUN0ZnBFdWJsajk0Y21lUUFBIiwidmVyIjoiMi4wIn0.FBu7OEUl2JsPu-qZJ5FNV4H4yCTtvxy8Pvxf0Yeyt7euPnV_JhqAFezSc9iHo8V3yLGcj_RR5-Msr5hgSqydZK0P3tHp1WcRjPq7Dz1RnzxeCmw8d_VjiVqmEsbrnKVwkaqpf5oeFZg6d-gPc6_RE5Bq8sRHmc6STJm4V0QlaxQDSspcw1QogSUpTK_61qWfA9jpg2vkinUaysy0-dpvQ-qJCYpBO3e88WbQmvhkNexwcWaJ3LKzM9l9Ir_mK-T_tZo8pyZfJIj8HYAkktOUk93lArLMHkQvH7mJkEruLnfoH12VWVcHxxPapQdCIjia3hYMNzlCHANFyBm8RoTvJA'
HEADER = {
    'X-Api-Key': '0337a9de-9340-4ee3-8d20-86fbc75b0c8e',
    'authorization': 'Bearer '+ token
    }

url = "http://localhost:8081/set_config_default"
# url = "https://mflowapiv3.jnj.com/aisi2deploymentapivpcxtest/set_config_default"
response = requests.post(url, headers=HEADER, json=config_req)

# url = "http://localhost:9090/get_config"
# response = requests.get(url, headers=HEADER)

# url = "http://localhost:9090/start_deploy"
# response = requests.post(url, headers=HEADER, json=reqs[3])

url = "http://localhost:8081/re_deploy"
# url = "https://mflowapiv3.jnj.com/aisi2deploymentapivpcxtest1/re_deploy"
response = requests.post(url, headers=HEADER)

# time.sleep(5)
# url = "http://localhost:9090/get_status"
# response = requests.get(url, headers=HEADER, json=reqs[3])

# url = "http://0.0.0.0:8080/upload_model"
# response = requests.post(url, headers=HEADER, json=upload_info)

print(response.json(), response.status_code)


