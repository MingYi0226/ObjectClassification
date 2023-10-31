import time
from utils.ilogger import logger

class func_wrapper(object):
    def __init__(self, *args):
        self.params = args
    
    def test_type(self, data):
        valid_types = [list, dict, str, int, float, tuple, set, bool, bytes]
        if type(data) in valid_types:
            return True
        return False

    def __call__(self, func):
        def core_func(*args, **kwargs):
            # prepare param list for log
            params = kwargs.copy()
            if len(args):
                params['args'] = [arg for arg in args if self.test_type(arg)]
            
            func_name = func.__name__
            if 'save_param' not in kwargs:
                kwargs['save_param'] = True
            if kwargs['save_param']:
                logger.debug(f'{func_name}: {str(params)}')
            
            start_time = time.time()
            try:
                res = func(*args, **dict(kwargs, func_name=func_name))
                func_status = 'Finished'
            except Exception as e:
                func_status = f'Failed: {e}'
                res = None
                if 'catch' in kwargs and kwargs['catch']:
                    raise Exception(e)
            finally:
                elapsed_time = time.time() - start_time
                logger.debug(f'{func_name}: {func_status} {elapsed_time:.2f}s')
            return res
        return core_func