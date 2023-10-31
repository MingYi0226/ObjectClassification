from test_cases import TestDeployment

if __name__ == '__main__':
    workspace = 'AISI_CANADA_WORKSPACE'
    env = 'PROD'
    request_id = 'C0DDC7E6-BF00-48BE-A4EF-B94E2CCDD05B'

    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiIwNzYwZTA2Ni1iNTZkLTQ2ZjQtOGY0Yy1jZmUzOGVmZmNhMGIiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vM2FjOTRiMzMtOTEzNS00ODIxLTk1MDItZWFmZGE2NTkyYTM1L3YyLjAiLCJpYXQiOjE2NjY4NTY2ODIsIm5iZiI6MTY2Njg1NjY4MiwiZXhwIjoxNjY2ODYwNTgyLCJhaW8iOiJBV1FBbS84VEFBQUFrdmVTVjRkM0pobTlsOFI0VnVvdStuQzRQdU83R3dFN25lbS90Vm40Zm1CMjZzUTFBWUVjZG5IRTFVQS82ZDZLWVUrbkhiRTA5N250THdOTTdqTk1CRzdlUnhjandUdzh2MzFPL1JiSU93KzYxL1REbHZLM3FLUDBOTi85QTRULyIsIm5hbWUiOiJDdSwgTWluZ3lpIFtKSkNVUyBOT04tSlx1MDAyNkpdIiwibm9uY2UiOiJmMTk5ZGJjMC04ZDQ5LTQzYTUtYTU2Yy0zY2FhYjNjYmYzOWQiLCJvaWQiOiI1NjRiNzllNi1lMGQyLTRiMDgtYmJjZi00ZWFmYzIxYWY1OTUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJNQ3UzQGl0cy5qbmouY29tIiwicmgiOiIwLkFRUUFNMHZKT2pXUklVaVZBdXI5cGxrcU5XYmdZQWR0dGZSR2owelA0NDdfeWdzRUFMWS4iLCJyb2xlcyI6WyJVc2VyIl0sInN1YiI6IjdQaVppU1VpNWlfc01xWHRwaW85MlVYWXBlUHZaSmRBWUVGOTFUbS12MXciLCJ0aWQiOiIzYWM5NGIzMy05MTM1LTQ4MjEtOTUwMi1lYWZkYTY1OTJhMzUiLCJ1dGkiOiIyaWlhTzVUTTgwbVhqdGtUNXktdkFBIiwidmVyIjoiMi4wIn0.QnbargtRqzjUefxQU2ZDLLc2PRT49oEzypjgpbyiQ1iktnaNdEn4lTAICOe4P-mpatLMqOv8WdycaGRoUya2FPxa3mWVmzASCwYfzsda13gmy0KJVTwSaIfqnvwhKX4dHeaHsW61q-1YGIqhcMfkjDpRYAtAIBr1XoFW5nE1CceO5raECcu4QoZLoqo0efyAk8JOHSb-nYTcxAcT4GX6BPa4jZuewCgtdYZu72MrIXVaZlFzOg_WMIaLF-41B6c8MkMdWyqxjYDE0dt2fMvcdeZEsJgk--HHw84p2uyyFsi9ACCg9g01EtoLr2FGYCpHogtNJcyZxjeIh4YTqxQ2OQ'
    test_deployment = TestDeployment(env, workspace)
    test_deployment.headers['authorization'] = 'Bearer ' + token

    if not test_deployment.config:
        print('Invalid config!')
        exit(0)

    tray_list = [
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
            "tray_id":"061751F9-C313-4D13-B62E-AD72EE9B22C0",
            "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
            "request_id": "4"
        },
        {
            "tray_id":"064DC81F-4B95-40DC-81D3-B0798F2BAF7B",
            "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
            "request_id": "5"
        }, # 
        {
            "tray_id":"074694BA-49A1-468C-BA92-534C71351896",
            "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
            "request_id": "6"
        },
        
        {
            "tray_id":"E81A1B3A-7EA7-4D03-8A18-8182DA23F350",
            "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
            "request_id": "7"
        },
        {
            "tray_id":"26F5EA42-F24C-4BDE-9694-92827BF7072B",
            "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
            "request_id": "8"
        },
        {
            "tray_id":"93AEB91A-93D5-4C04-9A3A-74FABCA31C99",
            "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
            "request_id": "9"
        }
    ]

    test_data = {
        'get_config': {
            'method': 'get',
            'param': {
            }
        },
        'start_deploy': {
            'method': 'post',
            'param': tray_list[0]
        },
        'get_status': {
            'method': 'get',
            'param': tray_list[0]
        },
        're_deploy': {
            'method': 'post',
            'param': {}
        },
        'get_copy_local_to_storage_state': {
            'method': 'get',
            'param': {
                'request_id': request_id
            }
        },
        'copy_local_to_storage': {
            'method': 'post',
            'param': {
                "site_tray_list": [
                    {
                        "tray_id": "02CD7716-6CE1-4E10-B20E-DEDC0AF3481B",
                        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC"    
                    },
                    {
                        "tray_id": "074694BA-49A1-468C-BA92-534C71351896",
                        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC"    
                    },

                    {
                        "tray_id": "E81A1B3A-7EA7-4D03-8A18-8182DA23F350",
                        "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC"    
                    }
                ],
                "request_id": "112",
                "sas_key":"https://aihub01allwus2.file.core.windows.net/aisi?sv=2020-10-02&st=2022-05-20T17%3A25%3A27Z&se=2023-05-21T17%3A25%3A00Z&sr=s&sp=rcwdl&sig=eOOkWlibULu11hCHIW%2BU%2BiPvXYVuD5YOhlgyB6U0nWM%3D",
                "local_path":"aisi_total/output",
                "hyperparameters":{
                    "lr": 0.005,
                    "momentum": 0.9,
                    "weight_decay": 0.0005,
                    "step_size": 3,
                    "gamma": 0.1,
                    "epochs": 10,
                    "threshold": 0.7,
                    "sample_strategy": "s1",
                    "repeat": 1,
                    "batch_size": 4,
                }
            }
        },
    }
    test_funcs = [
        'get_config',
        # 'start_deploy',
        # 'get_status',
        # 're_deploy',
        # 'get_copy_local_to_storage_state',
        # 'copy_local_to_storage'
    ]
    for func in test_funcs:
        if func not in test_data:
            print('Invalid endpoint name!')
            break
        test_deployment.call(func, test_data[func])