import globals
from fastapi import UploadFile
from aisi_score import score
# ####### Training #########
# request = {kkz
#     "filesharename": "models",
#     "filesharepklfoldername": "models_pkl",
#     "modelfilename": "aisi.pkl", 
#     "modelmatricsfoldername": "models_matrics",
#     "modelmatricsfilename": "aisi_metrics.json",
#     "modeldatafoldername": "models_data",
#     "callbackurl": "http://www.google.com",
#     "trainingdata":"/home/adminforall/notebooks/playground/team/ernesto/intake/input/siteid1/2FF88196-D9BA-4E98-987E-8EC7F9C881AE/annotations",
#     "hyperparam":{
#         "lr": 0.005,
#         "momentum": 0.9,
#         "weight_decay":0.0005,
#         "step_size": 3,
#         "gamma": 0.1,
#         "epochs": 1,
#         "threshold": 0.7,
#         "tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
#         "site_id":"siteid1",
#         "repeat": 4,
#         "batch_size": 4
#         }
# }
# aisi = aisi_model.AISI(request, train_flag =True)
# aisi.train()

####### Scoring #########
request = {
    "tray_id": "FC38CA1C-5513-4C64-8F20-BD96293127AA",
    "site_id": "8D527957-437C-4FF9-BBA1-0696ECB04AAC",
    "request_id": "suchi_test"
}
is_vpcx = "yes"
lst = [
    {
        "siteId":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "trayId":"FC38CA1C-5513-4C64-8F20-BD96293127AA"
    }
]
globals.set_site_tray_comb_lst(lst)
globals.output_path = "/home/adminforall/notebooks/playground/team/ming/2021-12-test/intake/output1"

test_file = "/home/adminforall/notebooks/playground/team/ming/2021-12-test/intake/input/8D527957-437C-4FF9-BBA1-0696ECB04AAC/FC38CA1C-5513-4C64-8F20-BD96293127AA/images/00000000.jpg"
file = {
    'file': (test_file, open(test_file, 'rb'), 'application/octet')
    }
img_file = UploadFile(test_file, open(test_file, 'rb'))
result = score(request, image_file=img_file, is_vpcx=is_vpcx)
print(result)