
def get_top_left_comp(json_data, classes):
    min_id = ''
    # min_x, min_y = json_data["width"], json_data["height"]
    min_dist = json_data["width"] + json_data["height"]
    for bbox in json_data["components"]:
        comp_id = bbox["componentId"]
        if not comp_id:
            continue
        if comp_id not in classes:
            continue
        
        x = bbox['xMin']
        y = bbox['yMin']
        # if min_x > x or min_y > y:
        if min_dist > (x+y):
            min_id = comp_id
            min_dist = x+y
            # min_x = x
            # min_y = y
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