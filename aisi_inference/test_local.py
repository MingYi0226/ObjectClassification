import requests
import json
import os

PORT = 8080
def post_config_all(url=f"http://localhost:{PORT}/config_all"):

    body = {
        "output_path": "/home/adminforall/notebooks/playground/team/linggih/aisi/intake/output/",
        "tracking_mode": "True",
        "site_tray_comb": [
            {
                "siteId": "siteid1",
                "trayId": "7141F261-D5CB-4D55-B510-A6C23A1936F8"
            }
        ]
    }

    headers = {
        'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()

def post_set_site_tray_id(
    url=f"http://localhost:{PORT}/set_site_tray_id",
    comb_list=[
            {
                "siteId": "siteid1",
                "trayId": "7141F261-D5CB-4D55-B510-A6C23A1936F8"
            }
        ]):

    body = comb_list

    headers = {
        'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()

def post_set_output_path(
    url=f"http://localhost:{PORT}/set_output_path",
    path="/home/adminforall/notebooks/playground/team/linggih/aisi/intake/output/"
    ):
    
    body = {
        "data": path
    }

    headers = {
        'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
    }

    response = requests.post(url, data=body, headers=headers)
    return response.json()

def post_set_tracking_mode(url=f"http://localhost:{PORT}/set_tracking_mode", mode=True):

    body = {
        'tracking_mode': mode
    }

    headers = {
        'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
    }

    response = requests.post(url, data=body, headers=headers)
    return response.json()

def post_refresh_cache(url="http://localhost:80/refresh_cache"):

    body = {}

    headers = {
        'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()

def post_score_real(
    url=f"http://localhost:{PORT}/score_real",
    img_base_path="/home/adminforall/notebooks/playground/team/linggih/aisi/intake/input/",
    img_path="siteid1/7141F261-D5CB-4D55-B510-A6C23A1936F8/images/RIC4570301--1624542207776-1.jpg",
    site_id="siteid1",
    tray_id="7141F261-D5CB-4D55-B510-A6C23A1936F8",
    request_id="linggih_dummy_inference"
    ):

    final_path = os.path.join(img_base_path, img_path)
    config={
        "tray_id": tray_id,
        "site_id": site_id,
        "request_id": request_id
    }
    file_obj = {'file': (final_path, open(final_path, 'rb'), 'application/octet')}

    headers = {
        'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'
    }

    response = requests.post(url, headers=headers, data={'data': json.dumps(config)}, files=file_obj)
    return response.json()

res = post_config_all()
print(res)
res = post_set_site_tray_id()
print(res)
res = post_set_output_path()
print(res)
res = post_set_tracking_mode()
print(res)
# res = post_refresh_cache()
# print(res)
res = post_score_real()
print(res)
