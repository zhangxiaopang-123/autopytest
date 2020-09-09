
from Service import read_yaml
import os

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_name = 'test'
symbol = 'trxusdt'
typ = 'step0'
eos = 'zhf'
usd = 'btc'
env = ['test', 'stg', 'online']


def environment(sex):
    """
    sex=0时返回测试环境
    sex=1时返回预发环境
    sex=2时返回线上环境
    :param sex:
    :return:
    """
    if sex == 0:
        key = read_yaml.read_()[env[0]]['access-key'].split(',')[0]
        secret = read_yaml.read_()[env[0]]['secret-key'].split(',')[0]
        api_key = read_yaml.read_()[env[0]]['access-key'].split(',')[1]
        secret_key = read_yaml.read_()[env[0]]['secret-key'].split(',')[1]
        host = read_yaml.read_()[env[0]]['host']
        ws = read_yaml.read_()[env[0]]['ws']
        return key, secret, api_key, secret_key, host, ws
    elif sex == 1:
        pass
    else:
        pass


def email():
    server = read_yaml.read_()[env[-1]]['server']
    sender = read_yaml.read_()[env[-1]]['sender']
    receiver = read_yaml.read_()[env[-1]]['receiver']
    emailusername = read_yaml.read_()[env[-1]]['emailusername']
    emailpassword = read_yaml.read_()[env[-1]]['emailpassword']
    return server, sender, receiver, emailusername, emailpassword



