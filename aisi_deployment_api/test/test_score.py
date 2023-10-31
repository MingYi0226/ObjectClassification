import requests
import json
import time

headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}
request1 = {
    "tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
    "site_id": "siteid1",
    "request_id": "ernesto_test_1"
}
request2 = {
    "tray_id": "5D2AAB94-3FEA-4703-AA41-E214A6D4817B",
    "site_id": "siteid1",
    "request_id": "ernesto_test_2"
}
request3 = {
    "tray_id": "4E3BB038-B427-4FD0-8E59-78F52CD850D5",
    "site_id": "siteid1",
    "request_id": "ernesto_test_3"
}
request4 = {
    "tray_id": "237B85B8-5319-465B-B8D5-F11FAF8CFBF4",
    "site_id": "siteid1",
    "request_id": "ernesto_test_4"
}

url = "http://20.190.17.134:80/score_real"
url = "https://mflowv1qa.westus2.cloudapp.azure.com/m49b5c896f955462b9fe5ac7e84318c0fm/score_real"
# url = "http://0.0.0.0:9091/score_real"
test_file_1 = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/2FF88196-D9BA-4E98-987E-8EC7F9C881AE/Images/RIC4550301--1624561546477-0.jpg"
test_file_2 = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/5D2AAB94-3FEA-4703-AA41-E214A6D4817B/Images/RIC0400302--1624558494806-0.jpg"
test_file_3 = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/4E3BB038-B427-4FD0-8E59-78F52CD850D5/Images/RIC4700101--1624483729395-0.jpg"

files_1 = {'file': (test_file_1, open(test_file_1, 'rb'), 'application/octet')}
files_2 = {'file': (test_file_2, open(test_file_2, 'rb'), 'application/octet')}
files_3 = {'file': (test_file_3, open(test_file_3, 'rb'), 'application/octet')}
files_4 = {'file': (test_file_2, open(test_file_2, 'rb'), 'application/octet')}
data1 = {'data': json.dumps(request1)}
data2 = {'data': json.dumps(request2)}
data3 = {'data': json.dumps(request3)}
data4 = {'data': json.dumps(request4)}

# print(json.dumps(request))
start_time = time.time()
response1 = requests.post(url, files=files_1, data=data1, headers=headers)
response2 = requests.post(url, files=files_2, data=data2, headers=headers)
response3 = requests.post(url, files=files_3, data=data3, headers=headers)
response4 = requests.post(url, files=files_4, data=data4, headers=headers)
print(time.time()-start_time)
print(response1.text)
# print(response2.text)
# print(response3.text)
# print(response4.text)