
from Service import read_yaml
import os
import logging
import time

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(basedir)
env_name = 'stg'  # 切换环境
sex = 0   # 返回环境对应得key、value
symbol = 'xrpusdt'
types = 'old'  # 选择验签方式,old为老得验签方式,new为新得验签方式
# user_id = 81297219
user_id = 69234152

currency = ['xrp', 'usdt']
# symbol = 'test100usdt'  # 行情计算


# db_host = read_yaml.read_()[env_name]['db']['host']
# db_user = read_yaml.read_()[env_name]['db']['user']
# db_password = read_yaml.read_()[env_name]['db']['password']
# db_port = read_yaml.read_()[env_name]['db']['port']
# db_database = read_yaml.read_()[env_name]['db']['database']


class Con:

    def now_time(self):
        now_time = int(time.time())
        return now_time

    def environment(self):
        key = read_yaml.read_()[env_name]['access-key'].split(',')[0]
        secret = read_yaml.read_()[env_name]['secret-key'].split(',')[0]
        api_key = read_yaml.read_()[env_name]['access-key'].split(',')[1]
        secret_key = read_yaml.read_()[env_name]['secret-key'].split(',')[1]
        host = read_yaml.read_()[env_name]['host']
        _host = read_yaml.read_()[env_name]['_host']
        if sex == 0:
            return key, secret, host, _host
        else:
            return api_key, secret_key, host, _host


    def sql(self):
        host = read_yaml.read_()[env_name]['db']['host']
        port = read_yaml.read_()[env_name]['db']['port']
        user = read_yaml.read_()[env_name]['db']['user']
        password = read_yaml.read_()[env_name]['db']['password']
        database = read_yaml.read_()[env_name]['db']['database']
        return host, user, password, port, database

    def info_log(self, post_data, url, response):
        log_path = os.path.join(basedir, r'Logs')
        # print('adad',log_path)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        logname = os.path.join(log_path, '%s-info.log' % time.strftime('%Y_%m_%d'))

        file = os.path.join(log_path, logname)
        # print('aa', file)
        logger = logging.getLogger()
        # logging.basicConfig(
        #     level=logging.INFO, format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        #     datefmt='%a, %d %b %Y %H:%M:%S', filename=file, filemode='a')
        # logger.info(post_data)
        # logger.info(url)
        # logger.info(response)
        # logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(logname, mode='a')
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger.info(post_data), logger.info(url), logger.info(response)

    def error_log(self, post_data, url, response):
        log_path = os.path.join(basedir, r'Logs')
        # print('adad',log_path)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        logname = os.path.join(log_path, '%s-error.log' % time.strftime('%Y_%m_%d'))

        file = os.path.join(log_path, logname)
        # print('aa', file)
        logger = logging.getLogger()
        # logging.basicConfig(
        #     level=logging.INFO, format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        #     datefmt='%a, %d %b %Y %H:%M:%S', filename=file, filemode='a')
        # logger.info(post_data)
        # logger.info(url)
        # logger.info(response)
        # logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(logname, mode='a')
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger.error(post_data), logger.error(url), logger.error(response)


if __name__ == '__main__':
    # Con().error_log('test', 'test', 'test')
    Con().info_log('test', 'test', 'test')


