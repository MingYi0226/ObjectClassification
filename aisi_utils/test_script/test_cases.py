from ast import arg
import requests
import os
import json


class func_wrapper(object):
    def __call__(self, func):
        def core_func(*args, **kwargs):
            header = args[0].api.upper() + '/' + args[1] + '()'
            print(f'============================= {header} START ====================================')
            func(*args)
            print(f'============================= {header} END   ====================================\n')
        return core_func

class TestCase:
    def __init__(self, env, workspace, api):
        self.env = env
        self.worksapce = workspace
        self.api = api

        # get basepath
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.base_path = os.path.join(base_path, 'config_set', f'aisi_{self.api}', self.env)

        if api == 'saa':
            self.headers = {'X-Api-Key': '896d35d2-a352-4705-b4f5-e8d86724fe52'}
        elif api == 'deployment':
            self.headers = {
                'X-Api-Key': '0337a9de-9340-4ee3-8d20-86fbc75b0c8e',
                'authorization': 'Bearer '
            }
        elif api == 'inference':
            self.headers = {'X-Api-Key': '46f3d27c-c8d4-11eb-b8bc-0242ac130003'}

    def get(self, url, pay_load={}):
        res = requests.get(url, headers=self.headers, json=pay_load)
        res = json.loads(res.text)
        res = json.dumps(res, indent=4)
        print(f'url: {url}\nparam:{json.dumps(pay_load, indent=4)}\nres: {res}')

    def post(self, url, pay_load={}):
        res = requests.post(url, headers=self.headers, json=pay_load)
        print(res.text)
        res = json.loads(res.text)
        
        res = json.dumps(res, indent=4)
        print(f'url: {url}\nparam:{json.dumps(pay_load, indent=4)}\nres: {res}')
    
    @func_wrapper()
    def call(self, func_name, func_param):
        try:
            end_point = f'{self.config["url"]}{func_name}'
            func = getattr(self, func_param['method'])
            func(end_point, func_param['param'])
        except Exception as e:
            print('Error:', e)


class TestSAA(TestCase):
    def __init__(self, env, workspace):
        super().__init__(env, workspace, 'saa')
        self.config = self.get_endpoint()

    def get_endpoint(self):
        config_path = os.path.join(self.base_path, 'config_all.json')
        config = None
        try:
            with open(config_path, 'r') as f:
                conf = json.load(f)
            for ws in conf['workspaces']:
                if ws['workspace'] == self.worksapce:
                    config = ws.copy()
                    break
        except Exception as e:
            print(e)
        return config



class TestDeployment(TestCase):
    def __init__(self, env, workspace):
        super().__init__(env, workspace, 'deployment')
        self.config = self.get_endpoint()

    def get_endpoint(self):
        config_path = os.path.join(self.base_path, 'config_all.json')
        config = None
        try:
            with open(config_path, 'r') as f:
                conf = json.load(f)
            for ws in conf['workspaces']:
                if ws['workspace'] == self.worksapce:
                    config = ws.copy()
                    break
        except Exception as e:
            print(e)
        return config


class TestInference(TestCase):
    def __init__(self, end_point):
        super().__init__('', '', 'inference')
        self.config = {
            'url': end_point
        }
