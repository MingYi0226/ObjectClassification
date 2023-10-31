import json, requests

if __name__ == '__main__':
    headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

    workspace = 'AISI-PORTUGAL-PROD'
    sample_trays = {
        'AISI-CANADA-QA': {
            'site_id': '8D527957-437C-4FF9-BBA1-0696ECB04AAC',
            'tray_id': '93AEB91A-93D5-4C04-9A3A-74FABCA31C99',
            'train_path': '/aisiqacanada/input'
        },
        'AISI-COLUMBIA-QA': {
            'site_id': 'FE7AFDDD-324B-4131-979C-C0EF3F1430C4',
            'tray_id': '0777C723-F4EE-4B28-A60A-A89809B5494D',
            'train_path': '/aisiqacolumbia/input'
            
        },
        'AISI-PORTUGAL-QA': {
            'site_id': '7CEFE80A-0F2E-415F-BAD0-5ABAD6F53E16',
            'tray_id': '012C3604-6EA7-4344-98BD-DC9D8D0617D9',
            'train_path': '/aisiqaportugal/input'
            
        },
        'AISI-TESTSITE-BST': {
            'site_id': '8D527957-437C-4FF9-BBA1-0696ECB04AAC',
            'tray_id': '93AEB91A-93D5-4C04-9A3A-74FABCA31C99',
            'train_path': '/aisibsttestsite/input'
        },
        'AISI-PORTUGAL-PROD': {
            'site_id': '7CEFE80A-0F2E-415F-BAD0-5ABAD6F53E16',
            'tray_id': '012C3604-6EA7-4344-98BD-DC9D8D0617D9',
            'train_path': '/aisiprodportugal/input'
        }
    }
    site_id = sample_trays[workspace]['site_id']
    tray_id = sample_trays[workspace]['tray_id']
    train_path = sample_trays[workspace]['train_path']

    # url =    "https://mflowqa.jnj.com/gw/management/api/algo/803fe421-f023-477b-9365-826819238496"
    url = "http://mflowstaging.jnj.com/gw/management/api/algo/950c1126-83e5-43f4-adfc-bbfb965f669a"
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiIwNzYwZTA2Ni1iNTZkLTQ2ZjQtOGY0Yy1jZmUzOGVmZmNhMGIiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vM2FjOTRiMzMtOTEzNS00ODIxLTk1MDItZWFmZGE2NTkyYTM1L3YyLjAiLCJpYXQiOjE2NzQxNjIwNjgsIm5iZiI6MTY3NDE2MjA2OCwiZXhwIjoxNjc0MTY1OTY4LCJhaW8iOiJBV1FBbS84VEFBQUE1MmV1NkxFZldmelhNQW5iQWpxazgvemNuYXlhYTB5QmxzL2pNOXQzUit3b1NJb1BSUXhqTWR2ZW9SazVxK0l6UEZjUDZGTTIzV2Evc2Uwc1BHdDkxZml5dGZ1cytCbjBCd1lRKzc1eEx0dzZpMlA3aWJSM1VQaGdLbnZGckhNNiIsIm5hbWUiOiJDdSwgTWluZ3lpIFtKSkNVUyBOT04tSlx1MDAyNkpdIiwibm9uY2UiOiJmMjE0NmI2Mi00ZGYyLTQwYjItOWFlYi0xZTY3ODdjNzdhMTYiLCJvaWQiOiI1NjRiNzllNi1lMGQyLTRiMDgtYmJjZi00ZWFmYzIxYWY1OTUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJNQ3UzQGl0cy5qbmouY29tIiwicmgiOiIwLkFRUUFNMHZKT2pXUklVaVZBdXI5cGxrcU5XYmdZQWR0dGZSR2owelA0NDdfeWdzRUFMWS4iLCJyb2xlcyI6WyJVc2VyIl0sInN1YiI6IjdQaVppU1VpNWlfc01xWHRwaW85MlVYWXBlUHZaSmRBWUVGOTFUbS12MXciLCJ0aWQiOiIzYWM5NGIzMy05MTM1LTQ4MjEtOTUwMi1lYWZkYTY1OTJhMzUiLCJ1dGkiOiJiN2pQQmsyOXVrLTJGRFlTU0tpVkFBIiwidmVyIjoiMi4wIn0.cVlU3Quh-t6rag8z4wDbCqrKm4USR84U464QWoKQC7lAneeKY-Pr8xKy9NWTZruYh-3oZS7YEbfCC5R27XOTV0AYQLUkWVxKKYUekvvK2LkdN1j7TcpD7hR69nJS9QqJLM4A_7cHvGI1J9-hGlv0YunBvK-T9E8f5SFWPK2WCTbFBcuTgTKe7EpZJwDFHYnKocoqTthVmGsXjDCbDXDiBYMDdQNYMfS3VVdmYxNhITyNUxAODKZlWZQhWL4HBFVg5C-6Z9-jmSvDyYozAyb4blG81h2un-0VD1Vthqz1HZwRa5yvY6eAmOt_OMdE_cxWkRdetjJhSZ1WqBg6313eWw'
    headers = {
        "authorization": "Bearer "+ token
    }
    params = {
        "trainingPath": train_path, 
        "HyperParameters": 
        {
            "lr":0.005,
            "momentum": 0.9,
            "weight_decay": 0.0005,
            "step_size": 3,
            "gamma": 0.1,
            "epochs": 1,
            "threshold": 0.71,
            "tray_id": tray_id,       
            "site_id":site_id,
            "repeat": 1,
            "batch_size":6
        }, 
        "IsCloudPath": True,
        "ramSize": 52,
        "core": 1, 
        "gpuCount": 1,
        "IsGpu": True
    }

    response = requests.post(url, headers=headers, json=params)
    print(response.text)