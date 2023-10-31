import json
import shutil
import os
import argparse
from PIL import ImageOps, Image

def make_default_autocomplete_metadata(opt):
    base_path = os.path.join(opt.input, "input")
    if not os.path.isdir(base_path):
        raise Exception("Invalid base path: ", base_path)
    
    
    for site_id in os.listdir(base_path):
        for tray_id in os.listdir(os.path.join(base_path, site_id)):
            json_dir = os.path.join(base_path, site_id, tray_id, "autocompletion")
            os.makedirs(json_dir, exist_ok=True)
            json_data = {
                'site_id': site_id,
                'tray_id': tray_id,
                'components': []
            }

            # get annotation path
            ann_dir = os.path.join(base_path, site_id, tray_id, "annotations")
            first_name = sorted(os.listdir(ann_dir))[0]
            ann_path = os.path.join(ann_dir, first_name)

            # read first annotation file
            with open(ann_path, 'r') as f:
                in_data = json.load(f)
            
            for comp in in_data['components']:
                json_data['components'].append({
                    'component_id': comp['componentId'],
                    'auto_type': 'Auto',
                    'sub_type': '',
                    'confidence_threshold': 70
                })
            
            with open(os.path.join(json_dir, 'autocompletion_metadata.json'), 'w') as f:
                json.dump(json_data, f, indent=4)
            print(f'site_id: {site_id} tray_id: {tray_id} processed successfully')            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    base_path = '/home/adminforall/notebooks/aisi/phase_2/data/ming/v2'
    # parse input arguments
    parser.add_argument('--input', type=str, default = base_path, help='base path for storage')
    opt = parser.parse_args()
    try:
        make_default_autocomplete_metadata(opt)
    except Exception as e:
        print(e)