from common import *

def set_inference_config(config_json, outputs):
    # set env variables
    for key in config_json['env_config']:
        os.environ[key] = config_json['env_config'][key]
    
    # get table name
    table_name = os.environ['AZURE_TABLE_NAME']
    
    # iterate workspaces
    for i, _ in enumerate(outputs):
        # get workspace name
        ws = _['workspace']

        # init variables
        endpoints = []
        is_successed = -1
        desc_msg = ''
        try:
            # get matched workspace from config
            matched_ws = get_matched_workspace(config_json, ws)

            # select one
            matched_ws = matched_ws[0]

            # read config
            conf = matched_ws['config']
            conn_str = matched_ws['connection_string_name']

            # validate conf
            if 'output_path' not in conf:
                raise Exception('output_path not found in config')

            if 'tracking_mode' not in conf:
                raise Exception('output_path not found in config')

            # get connection string
            table_conn_str = get_connection_string(conn_str)

            if not table_conn_str:
                raise Exception("Can not get table connection string. Please check out config file.")

            # fetch urls
            urls, res = get_urls_from_table(table_name, table_conn_str)

            if not res:
                raise Exception("Can not fetch from table. Please check out config file.")

            for url in urls:
                # init 
                _status = -1
                _desc = ''
                end_url = f'{url}config_all'

                # prepare inference config data
                config_data = conf
                config_data['site_tray_comb'] = urls[url]
                
                try:
                    response = requests.post(end_url, headers = INFERENCE_HEADER, json=config_data)
                    
                    # check response
                    res_code = response.status_code
                    if res_code == 200:
                        _status = 1
                        _desc = 'Set config completed'
                    else:
                        _desc = f"returned {res_code}"
                except Exception as e:
                    print(f'config_all() err: {e}')
                    _desc = f'{e}'
                endpoints.append({
                    'endpoint_address': end_url,
                    'endpoint_status': _status,
                    'endpoint_description': _desc
                })
            is_successed = 1

            if len(urls):
                desc_msg = 'Set config completed'
            else:
                desc_msg = 'No deployed urls were found.'
        except KeyError as e:
            desc_msg = f'{e} was not found'
        except Exception as e:
            desc_msg = f'{e}'
            print(f'{ws} err: {e}')
        
        # update output
        outputs[i]['endpoints'] = endpoints
        outputs[i]['status'] = is_successed
        outputs[i]['description'] = desc_msg
    return outputs