import json, requests
from test_cases import TestInference

if __name__ == '__main__':
    headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

    url = "https://deployment.mflowqa.jnj.com/mb90780ae5d514fdf8d80ef0aecc41ae8m/"
    site_id = "8D527957-437C-4FF9-BBA1-0696ECB04AAC"
    tray_id = "02CD7716-6CE1-4E10-B20E-DEDC0AF3481B"
    request_id = "test-5M"
    test_file = "D:/Test/93ae.jpg"
    
    test_inference = TestInference(url)
    test_data = {
        'score_real': {
            'method': 'get',
            'param': {
                "tray_id": tray_id,
                "site_id": site_id,
                "request_id": request_id
            }
        },
        'refresh_cache': {
            'method': 'post',
            'param': {

            }
        }
    }
    test_funcs = [
        'score_real',
        # 'refresh_cache'
    ]
    for func in test_funcs:
        if func not in test_data:
            print('Invalid endpoint name!')
            break
        if func == 'score_real':
            file = {'file': (test_file, open(test_file, 'rb'), 'application/octet')}
            data = {'data': json.dumps(test_data[func]['param'])}
            response = json.loads(requests.post(f'{url}score_real', files=file, data=data, headers=headers).text)
            print(json.dumps(response, indent=4))
        else:
            test_inference.call(func, test_data[func])