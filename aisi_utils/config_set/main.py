import json
import os
import argparse
from common import CONFIG_ALL
from aisi_deployment import set_deployment_config
from aisi_inference import set_inference_config
from aisi_saa import set_saa_config


def set_config(opt):
    # init output
    outputs = []
    is_processed = False
    try:
        # validate arguments
        if not opt.input:
            raise Exception('--input not specified')

        if not opt.output:
            raise Exception('--output not specified')
        
        if not opt.env:
            raise Exception('--env not specified')

        if not opt.api:
            raise Exception('--api not specified')

        # capitalize env name
        env = opt.env.upper()

        # convert to lowercase
        api = opt.api.lower()

        if env not in ['DEV', 'QA', 'PROD', 'INT', 'BST']:
            raise Exception('invalid --env argument')
        
        if api not in ['aisi_saa', 'aisi_deployment', 'aisi_inference']:
            raise Exception('invalid --api argument')

        # get input file path
        input_file_path = f'{opt.api}/{opt.env}/{opt.input}'

        # check input file is exist
        if not os.path.exists(input_file_path):
            raise Exception(f'{input_file_path} does not exist!')

        # get config_all json path
        config_file_path = f'{opt.api}/{opt.env}/{CONFIG_ALL}'

        # check config_all.json is exist
        if not os.path.exists(config_file_path):
            raise Exception(f'{config_file_path} does not exist!')
            
        is_processed = True

        # get workspaces from input
        try:
            with open(input_file_path, 'r') as f:
                input_json = json.load(f)
            workspaces = input_json['workspaces']

            # check if workspace name types
            is_str = True
            for _ in workspaces:
                if not isinstance(_, str):
                    is_str = False
                    break
                # init each workspace
                outputs.append({
                    'workspace': _,
                })
            if not is_str:
                raise Exception("workspace name is not string")

            if not len(workspaces):
                raise Exception(f'No workspaces was found in {input_file_path}')
        except Exception as e:
            print(f'Failed to parse {input_file_path}: {e}')
            raise Exception(f'Can not parse {input_file_path}')
        
        
        # open config json config_all file
        try:
            with open(config_file_path, 'r') as f:
                config_json = json.load(f)
        except Exception as e:
            print(f'Failed to parse {config_file_path}: {e}')
            raise Exception(f'Can not parse {config_file_path}')
        
        if api == 'aisi_inference':
            outputs = set_inference_config(config_json, outputs)
        elif api == 'aisi_saa':
            outputs = set_saa_config(config_json, outputs)
        elif api == 'aisi_deployment':
            outputs = set_deployment_config(config_json, outputs)
        
    except Exception as e:
        print(f'set_config err: {e}')
    finally:
        if is_processed:
            # save json into file
            output_file_path = f'{opt.api}/{opt.env}/{opt.output}'
            with open(output_file_path, 'w') as f:
                json.dump(outputs, indent=4, fp=f)
            
            # print saved path
            print(f'Output saved at {output_file_path}:\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # parse input arguments
    parser.add_argument('--input', type=str, default = 'input.json', help='List of workspaces')
    parser.add_argument('--output', type=str, default= 'output.json', help='output file of result')
    parser.add_argument('--env', type=str, default= 'DEV', help='set environment(DEV, PROD, QA, INT, BST')
    parser.add_argument('--api', type=str, default= 'aisi_deployment', help='select(aisi_saa, aisi_deployment, aisi_inference')
    opt = parser.parse_args()

    
    # call config_all()
    set_config(opt)