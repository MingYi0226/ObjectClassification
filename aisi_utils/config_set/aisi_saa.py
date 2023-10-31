from common import *

def set_saa_config(config_json, outputs):
    # iterate workspaces
    for i, _ in enumerate(outputs):
        # get workspace name
        ws = _['workspace']

        is_successed = -1
        desc_msg = ''
        try:
            # get matched workspace from config
            matched_ws = get_matched_workspace(config_json, ws)

            # select one
            matched_ws = matched_ws[0]

            # validate conf
            if 'url' not in matched_ws:
                raise Exception('url not found in config')
            if 'config' not in matched_ws:
                raise Exception('config not found in config')
            
            url = matched_ws['url']
            conf = matched_ws['config']

            end_url = f'{url}set_config'
            response = requests.post(end_url, headers = SAA_HEADER, json=conf)
                
            # check response
            res_code = response.status_code
            if res_code == 200:
                is_successed = 1
                desc_msg = 'Set config completed'
            else:
                desc_msg = f"returned {res_code}"
        except KeyError as e:
            desc_msg = f'{e} was not found'
            print(f'{ws} err: {desc_msg}')
        except Exception as e:
            desc_msg = f'{e}'
            print(f'{ws} err: {e}')
        # update output
        outputs[i]['status'] = is_successed
        outputs[i]['description'] = desc_msg
    return outputs