from fastapi.testclient import TestClient
from main import app
client = TestClient(app)


headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

def send_request(req_type, url, body={}):
    if req_type == 'get':
        res = client.get(url, headers=headers, json=body)
    elif req_type == 'post':
        res = client.post(url, headers=headers, json=body)
    else:
        return {}
    return res

def test_start_deploy_without_config():
    # test no config set
    param = {
        "tray_id":"",
        "site_id":"",
        "request_id": "1"
    }
    response = send_request('post', "/start_deploy", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/start_deploy", {})
    assert response.status_code == 422

def test_re_deploy_without_config():
    # test no config set
    param = {}
    response = send_request('post', "/re_deploy", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

def test_copy_local_to_storage_without_config():
    # test no config set
    param = {
        "site_tray_list": [
            {
                "tray_id": "site1",
                "site_id": "tray1"
            }
        ],
        "request_id": "111",
        "sas_key":"sas_key",
        "local_path":"foobar/output",
        "hyperparameters": {}
    }
    response = send_request('post', "/copy_local_to_storage", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/copy_local_to_storage", {})
    assert response.status_code == 422

def test_get_copy_local_to_storage_state_without_config():
    # test no config set
    param = {
        "request_id": "111"
    }
    response = send_request('get', "/get_copy_local_to_storage_state", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('get', "/get_copy_local_to_storage_state", {})
    assert response.status_code == 422


def test_get_status_without_config():
    # test no config set
    param = {
        "tray_id": "site1",
        "site_id": "tray1",
        "request_id": "111"
    }
    response = send_request('get', "/get_status", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('get', "/get_status", {})
    assert response.status_code == 422

def test_get_set_config():
    # test get
    response = send_request('get', '/get_config')
    assert response.status_code == 200
    assert response.json() == None

    # test not successful set
    param = {
        "connection_string_key_name": "key_name",
        "Name": "name",
        "output_path": "path",
        "tracking_mode": False,
        "workspace_name": "workspace name1",
        "project_name": "project 1",
        "capacity":1,
        "acrImage": {
            "Name": "name2",
            "ServicePort": "80",
            "ServiceName": "service1",
            "ImageUri": "url1",
            "DType": "type1",
            "deploymentForm": {
                "isGpu": True,
                "minMemory": 10,
                "maxMemory": 12,
                "cores":1
            }
        }
    }
    response = send_request('post', '/set_config_default', {})
    assert response.status_code == 422

    # test successful set
    response = send_request('post', '/set_config_default', param)
    assert response.status_code == 200
    assert response.json()['message'] == 'All configurations were properly set'

    # test get
    response = send_request('get', '/get_config')
    assert response.status_code == 200
    assert response.json() == param

def test_start_deploy():
    # test no config set
    param = {
        "tray_id":"",
        "site_id":"",
        "request_id": "1"
    }
    response = send_request('post', "/start_deploy", param)
    assert response.status_code == 200
    assert response.json()['message'] == 'connection string is wrong'

def test_re_deploy():
    # test no config set
    param = {}
    response = send_request('post', "/re_deploy", param)
    assert response.status_code == 200
    assert response.json()['message'] == 'redeployment has started'

def test_copy_local_to_storage():
    # test no config set
    param = {
        "site_tray_list": [
            {
                "tray_id": "site1",
                "site_id": "tray1"
            }
        ],
        "request_id": "111",
        "sas_key":"sas_key",
        "local_path":"foobar/output",
        "hyperparameters": {}
    }
    response = send_request('post', "/copy_local_to_storage", param)
    assert response.status_code == 200
    assert response.json()['message'] == 'Failed to copy'


def test_get_copy_local_to_storage_state():
    # test no config set
    param = {
        "request_id": "111"
    }
    response = send_request('get', "/get_copy_local_to_storage_state", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'


def test_get_status():
    # test no config set
    param = {
        "tray_id": "site1",
        "site_id": "tray1",
        "request_id": "111"
    }
    response = send_request('get', "/get_status", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'
