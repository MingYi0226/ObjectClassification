from test_cases import TestSAA
import uuid

if __name__ == '__main__':
    workspace = 'AISI-CANADA-QA'
    env = 'QA'
    sample_tray = '83AEB91A-93D5-4C04-9A3A-74FABCA31C99'

    sample_trays = {
        'AISI-CANADA-QA': {
            'site_id': '8D527957-437C-4FF9-BBA1-0696ECB04AAC',
            'tray_id': '83AEB91A-93D5-4C04-9A3A-74FABCA31C99'
        },
        'AISI-COLUMBIA-QA': {
            'site_id': 'FE7AFDDD-324B-4131-979C-C0EF3F1430C4',
            'tray_id': '0777C723-F4EE-4B28-A60A-A89809B5494D'
            
        },
        'AISI-PORTUGAL-QA': {
            'site_id': '7CEFE80A-0F2E-415F-BAD0-5ABAD6F53E16',
            'tray_id': '012C3604-6EA7-4344-98BD-DC9D8D0617D9'
            
        }
    }
    site_id = sample_trays[workspace]['site_id']
    tray_id = sample_trays[workspace]['tray_id']
    request_id = str(uuid.uuid4()).upper()

    test_data = {
        'get_config': {
            'method': 'get',
            'param': {}
        },
        'make_annotations': {
            'method': 'post',
            'param': {
                'path_name': f'secondary-test/{tray_id}/',
                'site_id': site_id,
                'tray_id': tray_id,
                'sas_key': 'https://mflowaisisite1vpcxqa.blob.core.windows.net/vpcxblob?sv=2020-08-04&st=2021-11-23T23%3A45%3A56Z&se=2022-11-24T23%3A45%3A00Z&sr=c&sp=racwdxlt&sig=hEFXM6dZ0dr7AazWbNELH8yU3QstQ1DUWg15sXMqI5Q%3D',
                'request_id': request_id
            }
        },
        'get_annotation_status': {
            'method': 'get',
            'param': {
                'request_id': request_id
            }
        },
        'start_download': {
            'method': 'post',
            'param': {
                'annotation_path_name': f'secondary-test/{sample_tray}/saa/annotations',
                'image_path_name': f'secondary-test/{sample_tray}/extracted_image',
                'site_id': site_id,
                'tray_id': tray_id,
                'sas_key': 'https://mflowaisisite1vpcxqa.blob.core.windows.net/vpcxblob?sv=2020-08-04&st=2021-11-23T23%3A45%3A56Z&se=2022-11-24T23%3A45%3A00Z&sr=c&sp=racwdxlt&sig=hEFXM6dZ0dr7AazWbNELH8yU3QstQ1DUWg15sXMqI5Q%3D',
                'request_id': request_id
            }
        },
        'get_download_status': {
            'method': 'get',
            'param': {
                'request_id': request_id
            }
        },
        'copy_config_data': {
            'method': 'post',
            'param': {
                "tray_id": tray_id,
                "site_id": site_id,
                "config": {   
                    "nms": 0.3,
                    "components": 
                    [
                        {
                            "component_id": "8B07D087-5C38-47A3-A56E-DB70CEA2A624",
                            "auto_type": "Auto",
                            "confidence_threshold": 70,
                            "sub_type": ""
                        },
                        {
                            "component_id": "7ECBF865-3F8A-4251-B57A-0829F9EDD9AC",
                            "auto_type": "Auto",
                            "confidence_threshold": 70,
                            "sub_type": ""
                        }
                    ]
                }
            }
        },
        'copy_nms_data': {
            'method': 'post',
            'param': {
                "site_id": site_id,
                "tray_id": tray_id,
                "nms": 0.3
            }
        },
        'copy_autocompletion_metadata': {
            'method': 'post',
            'param': {
                "site_id": site_id,
                "tray_id": tray_id,
                "request_id": request_id,
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
    }
    test_saa = TestSAA(env, workspace)

    if not test_saa.config:
        print('Invalid config data!')
        exit(0)
    
    test_funcs = [
        # 'get_config',
        'make_annotations',
        # 'get_annotation_status',
        # 'start_download',
        # 'get_download_status',
        # 'copy_config_data',
        # 'copy_nms_data',
        # 'copy_autocompletion_metadata'
    ]
    for func in test_funcs:
        if func not in test_data:
            print('Invalid endpoint name!')
            break
        test_saa.call(func, test_data[func])
