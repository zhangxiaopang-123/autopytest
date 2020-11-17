

import requests
import hashlib
import hmac
import json
import base64
from Service.config import Con
from Service import config


class Signature:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def share_sign(self, params, method, host, request_path):
        if config.env_name == 'test':
            host = host.replace('http://', '')
        else:
            host = host.replace('https://', '')
        qs0 = ''
        for key in sorted(params.keys()):
            qs0 += key + "=" + str(params[key]) + "&"
        qs0 = qs0[:-1]
        tmp = '%s\n%s\n%s\n%s' % (method.upper(), host, request_path, qs0)
        sign = hmac.new(self.secret_key.encode('utf-8'), msg=tmp.encode('utf-8'), digestmod=hashlib.sha256).digest()
        tmp = base64.b64encode(sign).decode()
        return tmp

    def sign(self, dic):
        tmp = ''
        for key in sorted(dic.keys()):
            tmp += key + str(dic[key])
        tmp += self.secret_key
        sign = hashlib.md5(tmp.encode()).hexdigest()
        return sign

    def get_sign(self, types, p, request_path, host):
        if types == 'old':
            si = self.sign(p)
            # print('请求老的验签方式:{}'.format(si))
        else:
            si = self.share_sign(p, 'GET', host, request_path)
            # print('请求新的验签方式:{}'.format(si))

        url = host + request_path
        # print("请求域名:{}".format(url))
        p['sign'] = si
        # print("请求参数:{}".format(p))
        try:
            res = requests.get(url=url, params=p)
            print('请求信息:{}'.format(res))
            Con().info_log(p, url, res)
            if res.status_code == 200:
                r = res.json()
                return r
        except Exception as e:
            Con().error_log(p, url, e)

    def post_sign(self, types, p, request_path, host):
        if types == 'old':
            si = self.sign(p)
            # print('请求老的验签方式:{}'.format(si))
        else:
            si = self.share_sign(p, 'POST', host, request_path)
            # print('请求新的验签方式:{}'.format(si))
        url = host + request_path
        # print("请求域名:{}".format(url))
        p['sign'] = si
        print("请求参数:{}".format(p))
        try:
            res = requests.post(url=url, data=p, headers={'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache"})
            print('response-code:{}'.format(res))
            Con().info_log(p, url, res)
            if res.status_code == 200:
                r = res.json()
                Con().info_log(p, url, r)
                return r
        except Exception as e:
            Con().error_log(p, url, e)










