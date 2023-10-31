from textwrap import indent
import requests
import json
import time

from requests import api

reqs = [
    {
        "tray_id":"02CD7716-6CE1-4E10-B20E-DEDC0AF3481B",
        "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "1"
    }, # 
    {
        "tray_id":"0424D78E-0B98-4C99-BB38-4D177524C07C",
        "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "2"
    }, # 
    {
        "tray_id":"059AEEB7-4F8E-414B-88E3-788CEA7EAB69",
        "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "3"
    }, # 
    {
        "tray_id":"064DC81F-4B95-40DC-81D3-B0798F2BAF7B",
        "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "4"
    }, # 
    {
        "tray_id":"074694BA-49A1-468C-BA92-534C71351896",
        "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "request_id": "5"
    }
]


config_req= {
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


token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiIwNzYwZTA2Ni1iNTZkLTQ2ZjQtOGY0Yy1jZmUzOGVmZmNhMGIiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vM2FjOTRiMzMtOTEzNS00ODIxLTk1MDItZWFmZGE2NTkyYTM1L3YyLjAiLCJpYXQiOjE2NTY1MjY3NTUsIm5iZiI6MTY1NjUyNjc1NSwiZXhwIjoxNjU2NTMwNjU1LCJhaW8iOiJBV1FBbS84VEFBQUFvOUFDb3dGYzkxWjd5RWVyK0tkNDZpeUtxY0tkQzZ2NVN6NWVnajlYNnpaZ2Q2bGt5SnFvaG5HdUdOZVIvT1pPRW9rRUJqVlNJT0YzTndGYi9SYWRPSDhwZHN3bVRhcktIcGpIWWtMeDFHQW93YlhPemgwUXRkU1Y4VTFiNEJpayIsIm5hbWUiOiJDdSwgTWluZ3lpIFtKSkNVUyBOT04tSlx1MDAyNkpdIiwibm9uY2UiOiJmNTA3ODhhYy0wMThhLTQzZjItYWM5Zi1iNzJhNzUwOWNhY2QiLCJvaWQiOiI1NjRiNzllNi1lMGQyLTRiMDgtYmJjZi00ZWFmYzIxYWY1OTUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJNQ3UzQGl0cy5qbmouY29tIiwicmgiOiIwLkFRUUFNMHZKT2pXUklVaVZBdXI5cGxrcU5XYmdZQWR0dGZSR2owelA0NDdfeWdzRUFMWS4iLCJyb2xlcyI6WyJVc2VyIl0sInN1YiI6IjdQaVppU1VpNWlfc01xWHRwaW85MlVYWXBlUHZaSmRBWUVGOTFUbS12MXciLCJ0aWQiOiIzYWM5NGIzMy05MTM1LTQ4MjEtOTUwMi1lYWZkYTY1OTJhMzUiLCJ1dGkiOiJaS2NRaG94NGIwaVlkSjVrUXZiZEFBIiwidmVyIjoiMi4wIn0.Fd1mUvAcU3m8UpBQ73FD3R2ibSh-d_e1wSkGrdbsgIUxmQz1ocW-V4UerZoJwFoBJpeyCrhO5uv-8iksJwKWUs8M9esrHEmdq0_oSur1EK7ETRGMr60xWYbvzmI8LpOIcGNmhNu9ABO4NQ5RMhb7SohmNQWr4pvYBjB-1-_7CnVZQSBqBXJjtnS2TVVMT237w8ZheEsYiUEbbp9LUm1-GxJbqx-jjpxNwSG5I1RfbIWiNKXkbUcuyu1BVyqPLGH5Wervf95POANbKvOxqEod_BnHqVO-ZCFuj4eVGARrYYU6lhURRbGpLEa922zmefjNggtsTTdcUPjqSfeDEkOq3Q'
HEADER = {
    'X-Api-Key': '0337a9de-9340-4ee3-8d20-86fbc75b0c8e',
    'authorization': 'Bearer '+ token
    }

# base = 'https://mflowapi.jnj.com/aisideploymentapi11012v'
# base = 'https://mflowapi.jnj.com/aisideploymentapitest'
base = 'https://deployment.mflowdev.jnj.com/aisideploymentapivpcxdev'

# url = f"{base}/set_config_default"
# response = requests.post(url, headers=HEADER, json=config_req)

# url = f"{base}/get_config"
# response = requests.get(url, headers=HEADER)

# url = f"{base}/start_deploy"
# response = requests.post(url, headers=HEADER, json=reqs[0])

# time.sleep(5)
# url = f"{base}/get_status"
# response = requests.get(url, headers=HEADER, json=reqs[0])

# url = "http://0.0.0.0:9090/algos"
# response = requests.get(url, headers=HEADER)

url = f"{base}/re_deploy"
response = requests.post(url, headers=HEADER)
print(response)
print(json.dumps(response.json(), indent=4))

