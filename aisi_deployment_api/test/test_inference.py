import requests
import json
########CONFIG ALL###########
headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}
config_req= {
    "output_path": "/aisisite1/output/",
    # "output_path": "/home/adminforall/notebooks/aisi/Phase 2/dev/ming/output/",
    "tracking_mode": "True",
    "site_tray_comb": [
        {
            "siteId": "siteid1",
            "trayId": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE"
        },
        {
            "siteId": "siteid1",
            "trayId": "5D2AAB94-3FEA-4703-AA41-E214A6D4817B"
        },
        {
            "siteId": "siteid1",
            "trayId": "4E3BB038-B427-4FD0-8E59-78F52CD850D5"
        },
        {
            "siteId": "siteid1",
            "trayId": "237B85B8-5319-465B-B8D5-F11FAF8CFBF4"
        }
    ]
    
}
url = "http://20.190.17.134:80/config_all"
# url = "http://0.0.0.0:9091/config_all"
response = requests.post(url, headers=headers, json=config_req)
print(response.text)
