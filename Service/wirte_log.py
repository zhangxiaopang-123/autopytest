import os
import logging
import time
import json
from Service import config


def return_log(post_data, url, response):
    cur_path = config.basedir
    log_path = os.path.join(cur_path, 'Log')
    if not os.path.exists(log_path): os.mkdir(log_path)
    logname = os.path.join(log_path, '%s.Log' % time.strftime('%Y_%m_%d'))
    file = os.path.join(log_path, logname)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S', filename=file, filemode='a')
    logger = logging.getLogger()
    return logger.info(post_data), logger.info(url), logger.info(response)

if __name__ =='__main__':
    return_log(1222,{'code': 1002, 'message': 'login-required', 'data': None})
