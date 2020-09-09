

import requests
import hashlib
import json
from Service import wirte_log


class Signature:
    def __init__(self, api_key, secret_key, tie):
        self.api_key = api_key
        self.secret_key = secret_key
        self.tie = tie

    def sign(self, dic):
        tmp = ''
        for key in sorted(dic.keys()):
            tmp += key + str(dic[key])
        tmp += self.secret_key
        sign = hashlib.md5(tmp.encode()).hexdigest()
        return sign

    def get_sign(self, request_path, host):
        p = {"api_key": self.api_key, "time": self.tie}
        # p.update(params)
        si = self.sign(p)
        url = host + request_path
        p['sign'] = si
        try:
            res = requests.get(url=url, params=p)
            if res.status_code == 200:
                r = res.json()
                wirte_log.return_log(p, url, r)
                return r
            else:
                wirte_log.return_log(p, url, res)
        except Exception as e:
            wirte_log.return_log(p, url, e)

    def get(self, request_path, host, p):
        params = {"api_key": self.api_key, "time": self.tie}
        p.update(params)
        si = self.sign(p)
        url = host + request_path
        p['sign'] = si
        try:
            res = requests.get(url=url, params=p)
            if res.status_code == 200:
                r = res.json()
                wirte_log.return_log(p, url, r)
                return r
            else:
                wirte_log.return_log(p, url, res)
        except Exception as e:
            wirte_log.return_log(p, url, e)

    def post_sign(self, p, request_path, host):
        url = host + request_path
        params = {"api_key": self.api_key, "time": self.tie}
        p.update(params)
        si = self.sign(p)
        p['sign'] = si
        # print("请求参数:{}".format(p))
        try:
            res = requests.post(url=url, data=p, headers={'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache"})
            if res.status_code == 200:
                r = res.json()
                wirte_log.return_log(p, url, r)
                return r
            else:
                wirte_log.return_log(p, url, res)
        except Exception as e:
            wirte_log.return_log(p, url, e)










