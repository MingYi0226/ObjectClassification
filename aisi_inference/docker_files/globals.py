from ilogger import logger
from threading import Semaphore
output_path = ""
site_tray_comb_lst = []
models = []
meta_data = []
semaphores = []
groups = []
categories = []

tracking_mode = True

def set_output_path(path):
    function_name = "set_output_path"
    global output_path
    output_path = path
    refresh_cache()
    logger.info(f'{function_name}: Cache refreshed and output_path set')

def set_tracking_mode(mode):
    function_name = "set_tracking_mode"
    global tracking_mode
    tracking_mode = mode
    logger.info(f'{function_name}: Tracking mode set')

def set_site_tray_comb_lst(lst):
    function_name = "set_set_tray_comb_lst"
    global site_tray_comb_lst
    global semaphores
    site_tray_comb_lst = lst
    # initialize them to empty list
    semaphores=[]
    for _ in site_tray_comb_lst:
        semaphores.append(Semaphore(value=1))
    logger.info(f'{function_name}: Site and tray id combination set')


def refresh_cache():
    function_name = refresh_cache
    ## What does refresh mapping does?
    global models
    global groups
    global categories
    global semaphores
    global meta_data
    
    if output_path == "":
        message = "Ask Administrator to set output path"
        logger.warning(f"{function_name}: {message}")
        return message

    models = []
    meta_data = []
    groups = []
    categories = []
    semaphores = []
    for _ in site_tray_comb_lst:
        semaphores.append(Semaphore(value=1))
    message = "Global variables successfully reset"
    logger.info(f"{function_name}: {message}")
    return message

