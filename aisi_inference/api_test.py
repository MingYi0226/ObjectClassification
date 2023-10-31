import requests
import json
import time

##########Set group id########
# url = "http://13.82.58.123:80/set_groups" 

# headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

# data = ["c2b5483a-ca0c-11eb-b8bc-0242ac130003", "72960565-2e47-4b6c-b16b-31360628b7d3"]
# response = requests.post(url,  json=data, headers=headers)
# print(response.text)

# ##########Set meta path########
# url = "http://13.82.58.123:80/set_meta_path" 

# headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

# data = {'data': "/models/models_data/aisi/pilot/experiment/experiment.json"}
# response = requests.post(url,  data=data, headers=headers)
# print(response.text)

# ##########Set tracking########
# url = "http://13.82.58.123:80/set_tracking_mode" 

# headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

# data = {'tracking_mode': True}
# response = requests.post(url,  data=data, headers=headers)
# print(response.text)

########SCORING###########
headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}
request1 = {
    "tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
    "site_id": "siteid1",
    "request_id": "ernesto_test_1"
}

request2 = {
    "tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
    "site_id": "siteid1",
    "request_id": "ernesto_test_2"
}

request3 = {
    "tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
    "site_id": "siteid1",
    "request_id": "ernesto_test_3"
}

# parameters for local VM - D15EB668-D538-4F45-98B4-748B77388B8B
url = "http://localhost:8082/score_real"
test_file_1 = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/2FF88196-D9BA-4E98-987E-8EC7F9C881AE/Images/RIC4550301--1624561546477-0.jpg"
test_file_2 = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/2FF88196-D9BA-4E98-987E-8EC7F9C881AE/Images/RIC4550301--1624561546477-0.jpg"
test_file_3 = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/2FF88196-D9BA-4E98-987E-8EC7F9C881AE/Images/RIC4550301--1624561546477-0.jpg"

# # parameters for MFlow Labx QA - D15EB668-D538-4F45-98B4-748B77388B8B
# url = "http://mflowv1qa.westus2.cloudapp.azure.com/aisi2/score_real"
# test_file = "test.jpg"

# # parameters for MFlow VPCx Prod - D15EB668-D538-4F45-98B4-748B77388B8B
# url = "http://10.75.152.35/score_real"
# test_file = "RIC5210301_3-6-2021_1543558.jpg"

# # parameters for  MFlow VPCx Prod - B1622D36-02BC-4C03-9F23-774EA0375256
# url = "http://10.75.152.49/score_real"
# test_file = "/Users/suchig/Downloads/RIC4500101--1624474800818-4.jpg"

# When working with concurrent requests, you cannot use the same datastream open(file) for both files
files_1 = {'file': (test_file_1, open(test_file_2, 'rb'), 'application/octet')}
files_2 = {'file': (test_file_2, open(test_file_2, 'rb'), 'application/octet')}
files_3 = {'file': (test_file_3, open(test_file_3, 'rb'), 'application/octet')}

data1 = {'data': json.dumps(request1)}
data2 = {'data': json.dumps(request2)}
data3 = {'data': json.dumps(request3)}

# print(json.dumps(request))
start_time = time.time()
response1 = requests.post(url, files=files_1, data=data1, headers=headers)
#response2 = requests.post(url, files=files_2, data=data2, headers=headers)
#response3 = requests.post(url, files=files_3, data=data3, headers=headers)

print(time.time()-start_time)
print(response1.text)
#print(response2.text)
#print(response3.text)


# ########CONFIG ALL###########
# headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

# config_req= {
#     "output_path": "/home/adminforall/notebooks/playground/team/ernesto/intake/output/",
#     "tracking_mode": "True",
#     "site_tray_comb": [
#         {
#             "siteId": "siteid1",
#             "trayId": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE"
#         },
#         {
#             "siteId": "siteid2",
#             "trayId": "D15EB668-D538-4F45-98B4-748B77388B8B"
#         }
#     ]
# }
# url = "http://localhost:8080/config_all"
# response = requests.post(url, headers=headers, json=config_req)

# print(response.text)
