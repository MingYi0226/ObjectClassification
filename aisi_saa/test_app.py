from fastapi.testclient import TestClient
from app import app
client = TestClient(app)

headers = {'X-Api-Key': '896d35d2-a352-4705-b4f5-e8d86724fe52'}

def send_request(req_type, url, body={}):
    if req_type == 'get':
        res = client.get(url, headers=headers, json=body)
    elif req_type == 'post':
        res = client.post(url, headers=headers, json=body)
    else:
        return {}
    return res


def test_make_annotations_without_config():
    # test no config set
    param = {
        'path_name': 'path1',
        'site_id': 'siteid1',
        'tray_id': 'trayid1',
        'sas_key': 'sas_key',
        'request_id': 'req1'
    }
    response = send_request('post', "/make_annotations", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/make_annotations", {})
    assert response.status_code == 422


def test_get_annotation_status_without_config():
    # test no config set
    param = { 'request_id': 'req1'}
    response = send_request('get', "/get_annotation_status", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('get', "/get_annotation_status", {})
    assert response.status_code == 422


def test_get_download_status_without_config():
    # test no config set
    param = { 'request_id': 'req1'}
    response = send_request('get', "/get_download_status", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('get', "/get_download_status", {})
    assert response.status_code == 422


def test_start_download_without_config():
    # test no config set
    param = { 
        'annotation_path_name': 'annotation_path1',
        'image_path_name': 'imgage_path_name',
        'site_id': 'site_id',
        'tray_id': 'tray_id',
        'sas_key': 'https://foo.bar',
        'request_id': 'request_id'
    }
    response = send_request('post', "/start_download", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/start_download", {})
    assert response.status_code == 422


def test_copy_autocompletion_metadata_without_config():
    # test no config set
    param = { 
        "site_id": 'site_id',
        "tray_id": 'tray_id',
        "request_id": 'request_id',
        "components": [
            {
                "component_id": "AA5E0B1A-4AD8-4BF2-BB5F-F3928E6937C1",
                "auto_type": "Auto",
                "confidence_threshold": 70,
                "sub_type": ""
            },
            {
                "component_id": "E962BDC5-7B3F-470C-BA9F-78C2438AEC44",
                "auto_type": "Auto",
                "confidence_threshold": 70,
                "sub_type": ""
            }
        ]
    }
    response = send_request('post', "/copy_autocompletion_metadata", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/copy_autocompletion_metadata", {})
    assert response.status_code == 422


def test_copy_nms_data_without_config():
    # test no config set
    param = { 
        "site_id": 'site_id',
        "tray_id": 'tray_id',
        "nms": 0.3
    }
    response = send_request('post', "/copy_nms_data", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/copy_nms_data", {})
    assert response.status_code == 422


def test_copy_config_data_without_config():
    # test no config set
    param = { 
        "site_id": 'site_id',
        "tray_id": 'tray_id',
        "config": {   
            "nms": 0.3,
            "components": [
                {
                    "component_id": "AA5E0B1A-4AD8-4BF2-BB5F-F3928E6937C1",
                    "auto_type": "Auto",
                    "confidence_threshold": 70,
                    "sub_type": ""
                },
                {
                    "component_id": "E962BDC5-7B3F-470C-BA9F-78C2438AEC44",
                    "auto_type": "Auto",
                    "confidence_threshold": 70,
                    "sub_type": ""
                }
            ]
        }
    }
    response = send_request('post', "/copy_config_data", param)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Configure was not set. Please call /set_config()'

    response = send_request('post', "/copy_config_data", {})
    assert response.status_code == 422

def test_get_set_config():
    # test get
    response = send_request('get', '/get_config')
    assert response.status_code == 200
    assert response.json()['message'] == ''

    # test not successful set
    param = {
        "file_share_path": "/aisidevcanada/input",
        "total_thread": 5
    }
    response = send_request('post', '/set_config', param)
    assert response.status_code == 422

    # test successful set
    param = {
        "connection_string_key_name": "test_key",
        "file_share_path": "/workspace_name/input",
        "total_thread": 5
    }
    response = send_request('post', '/set_config', param)
    assert response.status_code == 200
    assert response.json()['message'] == 'connection string name was successfully set'

    # test get
    response = send_request('get', '/get_config')
    assert response.status_code == 200
    assert response.json()['message'] == param['connection_string_key_name']


def test_make_annotations():
    # test no config set
    config = {
        'path_name': 'secondary-test/93AEB91A-93D5-4C04-9A3A-74FABCA31C99/',
        'site_id': '8D527957-437C-4FF9-BBA1-0696ECB04AAC',
        'tray_id': '93AEB91A-93D5-4C04-9A3A-74FABCA31C99',
        'sas_key': 'https://mflowaisisite1vpcxqa.blob.core.windows.net/vpcxblob?sv=2020-08-04&st=2021-11-23T23%3A45%3A56Z&se=2022-11-24T23%3A45%3A00Z&sr=c&sp=racwdxlt&sig=hEFXM6dZ0dr7AazWbNELH8yU3QstQ1DUWg15sXMqI5Q%3D',
        'request_id': 'C0DDC7E6-BF00-48BE-A4EF-B94E2CCDD05B'
    }
    response = send_request('post', "/make_annotations", {})
    assert response.status_code == 422

    response = send_request('post', "/make_annotations", config)
    assert response.status_code == 200
    assert response.json()['message'] == 'making annotations has started'
    

def test_get_annotation_status():
    param = { 'request_id': 'req1'}
    response = send_request('get', "/get_annotation_status", param)
    assert response.status_code == 200
    assert 'last_update' in response.json()
    assert 'description' in response.json()
    assert 'status' in response.json()
    assert 'start_time' in response.json()
    assert 'finish_time' in response.json()


def test_get_download_status():
    param = { 'request_id': 'req1'}
    response = send_request('get', "/get_download_status", param)
    print(response.json())
    assert response.status_code == 200
    assert 'description' in response.json()
    assert 'status' in response.json()
    assert 'start_time' in response.json()
    assert 'finish_time' in response.json()
    assert 'training_path' in response.json()


def test_start_download():
    # test no config set
    param = { 
        'annotation_path_name': 'annotation_path1',
        'image_path_name': 'imgage_path_name',
        'site_id': 'site_id',
        'tray_id': 'tray_id',
        'sas_key': 'https://foo.bar',
        'request_id': 'request_id'
    }
    response = send_request('post', "/start_download", param)
    assert response.status_code == 200
    assert response.json()['message'] == 'download started'


def test_copy_autocompletion_metadata():
    # test no config set
    param = { 
        "site_id": 'site_id',
        "tray_id": 'tray_id',
        "request_id": 'request_id',
        "components": [
            {
                "component_id": "AA5E0B1A-4AD8-4BF2-BB5F-F3928E6937C1",
                "auto_type": "Auto",
                "confidence_threshold": 70,
                "sub_type": ""
            },
            {
                "component_id": "E962BDC5-7B3F-470C-BA9F-78C2438AEC44",
                "auto_type": "Auto",
                "confidence_threshold": 70,
                "sub_type": ""
            }
        ]
    }
    response = send_request('post', "/copy_autocompletion_metadata", param)
    assert response.status_code == 200
    print(response.json())
    assert 'status' in response.json()


def test_copy_nms_data():
    # test no config set
    param = { 
        "site_id": 'site_id',
        "tray_id": 'tray_id',
        "nms": 0.3
    }
    response = send_request('post', "/copy_nms_data", param)
    assert response.status_code == 200
    assert 'status' in response.json()


def test_copy_config_data():
    # test no config set
    param = { 
        "site_id": 'site_id',
        "tray_id": 'tray_id',
        "config": {   
            "nms": 0.3,
            "components": [
                {
                    "component_id": "AA5E0B1A-4AD8-4BF2-BB5F-F3928E6937C1",
                    "auto_type": "Auto",
                    "confidence_threshold": 70,
                    "sub_type": ""
                },
                {
                    "component_id": "E962BDC5-7B3F-470C-BA9F-78C2438AEC44",
                    "auto_type": "Auto",
                    "confidence_threshold": 70,
                    "sub_type": ""
                }
            ]
        }
    }
    response = send_request('post', "/copy_config_data", param)
    assert response.status_code == 200
    assert 'status' in response.json()