import json
import shutil
import os
import argparse
from PIL import ImageOps, Image

def get_top_left_comp(json_data, classes):
    min_id = ''
    min_x, min_y = json_data["width"], json_data["height"]
    for bbox in json_data["components"]:
        comp_id = bbox["componentId"]
        if not comp_id:
            continue
        if comp_id not in classes:
            continue
        
        x = bbox['xMin']
        y = bbox['yMin']
        if min_x > x or min_y > y:
            min_id = comp_id
            min_x = x
            min_y = y
    return min_id

'''
    Returns component position in the image
    0 - Top Left
    1 - Top Right
    2 - Bottom Left
    3 - Bottom Right
'''
def get_compo_pos(json_data, comp_id):
    bbox = [comp for comp in json_data["components"] if comp["componentId"]==comp_id]
    if len(bbox) == 0:
        return -1
    bbox = bbox[0]
    x, y = bbox['xMin'], bbox['yMin']
    midddle_x, middle_y = int(json_data["width"])//2, int(json_data["height"])//2
    
    pos = 0
    if x >= midddle_x:
        pos = 1 if y < middle_y else 3
    else:
        pos = 0 if y < middle_y else 2
    return pos

# returns number of different characters of two strings
def compare_strings(a, b):
    if a is None or b is None:
        print("Number of Same Characters: 0")
        return
    
    size = min(len(a), len(b)) # Finding the minimum length
    count = 0 # A counter to keep track of same characters

    for i in range(size):
        if a[i] != b[i]:
            count += 1 # Updating the counter when characters are same at an index

    return count

def copy_reference_images(opt):
    base_path = os.path.join(opt.input, "input")
    if not os.path.isdir(base_path):
        raise Exception("Invalid base path: ", base_path)
    
    output_path = os.path.join(opt.input, "output")
    for site_id in os.listdir(base_path):
        for tray_id in os.listdir(os.path.join(base_path, site_id)):
            img_path = os.path.join(base_path, site_id, tray_id, "images")
            ann_path = os.path.join(base_path, site_id, tray_id, "annotations")
            
            file_list = sorted(os.listdir(img_path))
            if len(file_list) == 0:
                print(f'ERROR=> site_id: {site_id} tray_id: {tray_id} : images not found')
                continue
            
            # copy 0 degree image
            first_name = file_list[0]
            src_path = os.path.join(img_path, first_name)

            dst_dir = os.path.join(output_path, site_id, tray_id, "reference", "images") 
            os.makedirs(dst_dir, exist_ok=True)
            
            img = Image.open(src_path).convert("RGB")
            img = ImageOps.exif_transpose(img)
            dst_path_0 = os.path.join(dst_dir, "reference_image_0.jpg")
            dst_img_path_180 = os.path.join(dst_dir, "reference_image_180.jpg")
            # img.save(dst_path_0)
            print(f'{src_path} => {dst_path_0}')

            # copy 0 degree annotation
            first_name = first_name[:-4] + ".json"
            src_path = os.path.join(ann_path, first_name)

            dst_dir = os.path.join(output_path, site_id, tray_id, "reference", "annotations")
            os.makedirs(dst_dir, exist_ok=True)
            
            dst_path_0 = os.path.join(dst_dir, "reference_annotation_0.json")
            dst_json_path_180 = os.path.join(dst_dir, "reference_annotation_180.json")
            with open(src_path, 'r') as fr, open(dst_path_0, 'w') as fw0:
                json_data_0 = json.load(fr)
                # json.dump(json_data_0, fw0, indent=4)
            print(f'{src_path} => {dst_path_0}')

            # get top-left component id
            categories = [comp['componentId'] for comp in json_data_0["components"] if comp['componentId']]
            
            top_left_id = get_top_left_comp(json_data_0, categories)
            if not top_left_id:
                print(f'ERROR=> site_id: {site_id} tray_id: {tray_id} : top-left component not found')
                continue
            first_comp_pos = get_compo_pos(json_data_0, top_left_id)
            if first_comp_pos < 0:
                print(f'ERROR=> site_id: {site_id} tray_id: {tray_id} : top-left component invalid')
                continue
            print('top left component:', top_left_id, first_comp_pos)

            is_180_found = False
            json_data_180 = {}
            image_path_180 = ''
            current_file_name = file_list[0]
            for file_name in file_list[1:]:
                if compare_strings(current_file_name, file_name) <= 2:
                    current_file_name = file_name
                    continue
                current_file_name = file_name

                tmp_path = os.path.join(ann_path, file_name[:-4] + ".json")
                with open(tmp_path, 'r') as fr:
                    json_data_tmp = json.load(fr)
                new_pos = get_compo_pos(json_data_tmp, top_left_id)
                if new_pos < 0:
                    continue
                print(f'{file_name} - {top_left_id} - {new_pos}', end='\r')
                if new_pos == first_comp_pos:
                    continue
                is_180_found = True
                print('First 180 image found:', file_name)
                json_data_180 = json_data_tmp
                image_path_180 = os.path.join(img_path, file_name)
                break

            if is_180_found:
                # save found image as 180-degre image
                shutil.copyfile(image_path_180, dst_img_path_180)
                # save found json as 180-degree annotation
                with open(dst_json_path_180, 'w') as fw0:
                    json.dump(json_data_180, fw0, indent=4)
            else:
                print("180 degree image was not found, will rotate 0-degree image")
                # save 180 degree rotated image
                img.rotate(180).save(dst_img_path_180)
                print(f'{src_path} => {dst_img_path_180}')

                # save 180 degree rotated annotation
                width = json_data_0["width"]
                height = json_data_0["height"]
                for i, comp in enumerate(json_data_0["components"]):
                    x1 = width - comp["xMax"]
                    y1 = height - comp["yMax"]
                    x2 = width - comp["xMin"]
                    y2 = height - comp["yMin"]

                    json_data_0["components"][i]["xMin"] = x1
                    json_data_0["components"][i]["yMin"] = y1
                    json_data_0["components"][i]["xMax"] = x2
                    json_data_0["components"][i]["yMax"] = y2

                with open(dst_json_path_180, 'w') as fw180:
                    json.dump(json_data_0, fw180, indent=4)
                print(f'{src_path} => {dst_json_path_180}')

            print(f'site_id: {site_id} tray_id: {tray_id} processed successfully')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    base_path = '/home/adminforall/notebooks/aisi/phase_2/data/ming/v2'
    
    # parse input arguments
    parser.add_argument('--input', type=str, default = base_path, help='base path for storage')
    opt = parser.parse_args()
    try:
        copy_reference_images(opt)
    except Exception as e:
        print(e)