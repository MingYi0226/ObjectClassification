import aisi_model

####### Training #########
request = {
    "filesharename": "models",
    "filesharepklfoldername": "models_pkl",
    "modelfilename": "aisi.pkl", 
    "modelmatricsfoldername": "models_matrics",
    "modelmatricsfilename": "aisi_metrics.json",
    "modeldatafoldername": "models_data",
    "callbackurl": "http://www.google.com",
    "trainingdata":"/home/adminforall/notebooks/aisi/phase_2/data/ming/input/",
    "hyperparam":{
        "lr": 0.005,
        "momentum": 0.9,
        "weight_decay":0.0005,
        "step_size": 3,
        "gamma": 0.1,
        "epochs": 1,
        "threshold": 0.7,
        "tray_id": "26F5EA42-F24C-4BDE-9694-92827BF7072B",
        "site_id":"8D527957-437C-4FF9-BBA1-0696ECB04AAC",
        "repeat": 1,
        "batch_size": 4
        }
}
aisi = aisi_model.AISI(request)
aisi.train()

# ####### Scoring #########
# request = {
#     "tray_id": "2FF88196-D9BA-4E98-987E-8EC7F9C881AE",
#     "site_id": "siteid1",
#     "request_id": "suchi_test"
# }
# is_vpcx = "yes"
# globals.site_tray_comb_lst = [{"siteId":"siteid1",
#                             "trayId":"2FF88196-D9BA-4E98-987E-8EC7F9C881AE"}]
# globals.output_path = "/home/adminforall/notebooks/playground/team/ernesto/intake/output"
# test_file = "/home/adminforall/notebooks/playground/team/ernesto/intake/Input/SiteId1/2FF88196-D9BA-4E98-987E-8EC7F9C881AE/Images/RIC4550301--1624561546477-0.jpg"
# file = {'file': (test_file, open(test_file, 'rb'), 'application/octet')}
# img_file= UploadFile(test_file, open(test_file, 'rb'))
# result = score(request, image_file=img_file, is_vpcx=is_vpcx)
