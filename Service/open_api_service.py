from Service import wbf_signature
import requests
from Service.config import environment
from Service import config
import time
from Service import wirte_log


class Order:
    def market_depth(self, sym, typ, sex):
        """
        获取市场买卖盘
        :return:
        """
        request_path = '/open/api/market_dept'
        host = environment(config.env_name, sex)[-2]
        # print(host)
        url = host + request_path
        print(url)
        params = {"symbol": sym, "type": typ}
        print(params)
        try:
            res = requests.get(url=url, params=params)
            # print(res)
            if res.status_code == 200:
                r = res.json()
                wirte_log.return_log(params, url, r)
                print(r)
                return r
            else:
                wirte_log.return_log(params, url, res)
        except Exception as e:
            # print('error：{}'.format(e))
            wirte_log.return_log(params, url, e)

    def lastprice(self, symbol, sex):
        """
        获取最新成交价
        :param symbol:
        :return:
        """
        url = environment(config.env_name, sex)[-2] + '/open/api/market'
        # print(url)
        params = {"symbol": symbol}
        # print(params)
        try:
            result = requests.get(url, params=params)
            if result.status_code == 200:
                last_price = result.json()['data'][symbol]
                wirte_log.return_log(params,url, last_price)
                print(last_price)
                return last_price
            else:
                wirte_log.return_log(params, url, result)
        except Exception as e:
            print("error:{}".format(e))

    def order_place(self, p, data):
        """
        创建订单
        :param p:
        :return:
        """
        api_key = environment(config.env_name, data)[0]
        secret_key = environment(config.env_name, data)[1]
        host = environment(config.env_name, data)[-2]
        # print(api_key)
        tie = int(time.time())
        request_path = '/open/api/create_order'
        result = wbf_signature.Signature(api_key, secret_key, tie).post_sign(p, request_path, host)
        print(result)
        return result

    def order_place_all(self, p, data):
        """
        批量创建订单
        :param p:
        :return:
        """
        api_key = environment(config.env_name, data)[0]
        secret_key = environment(config.env_name, data)[1]
        host = environment(config.env_name, data)[-2]
        # print(host)
        tie = time.time()
        request_path = '/open/api/create_order'
        result = wbf_signature.Signature(api_key, secret_key, tie).post_sign(p, request_path, host)
        print(result)
        return result

    def order_cancel(self, p, data):
        """
        撤销订单
        :param p:
        :return:
        """
        api_key = environment(config.env_name, data)[0]
        secret_key = environment(config.env_name, data)[1]
        host = environment(config.env_name, data)[-2]
        # print(host)
        tie = int(time.time())
        request_path = '/open/api/cancel_order'
        result = wbf_signature.Signature(api_key, secret_key, tie).post_sign(p, request_path, host)
        print(result)
        return result

    def order_all_cancel(self, p, data):
        """
        批量撤销订单
        :param p:
        :return:
        """
        api_key = environment(config.env_name, data)[0]
        secret_key = environment(config.env_name, data)[1]
        host = environment(config.env_name, data)[-2]
        # print(host)
        tie = int(time.time())
        request_path = '/open/api/cancel_order_all'
        result = wbf_signature.Signature(api_key, secret_key, tie).post_sign(p, request_path, host)
        print(result)
        return result

    def account_balance(self, data, currency):
        """
        查询账户资产
        :return:
        """
        api_key = environment(data)[0]
        secret_key = environment(data)[1]
        host = environment(data)[-2]
        # print(host)
        tie = int(time.time())
        request_path = '/open/api/user/account'
        result = wbf_signature.Signature(api_key, secret_key, tie).get_sign(request_path, host)
        # print(result)
        coin = result['data']['coin_list']
        # print(coin)
        for i in range(0, len(coin)):
            if coin[i]['coin'] == currency:
                # print(coin[i]['normal'], coin[i]['locked'])
                wirte_log.return_log(currency, coin[i]['normal'], coin[i]['locked'])
                # print(coin[i]['normal'], coin[i]['locked'])
                return coin[i]['normal'], coin[i]['locked']

    def order_detail(self, p, data):
        """
        订单详情
        :return:
        """
        api_key = environment(config.env_name, data)[0]
        secret_key = environment(config.env_name, data)[1]
        host = environment(config.env_name, data)[-2]
        # print(host)
        tie = int(time.time())
        request_path = '/open/api/order_info'
        result = wbf_signature.Signature(api_key, secret_key, tie).get(request_path, host, p)
        return result


if __name__ == '__main__':
    Order().lastprice('zhfbtc', 0)
    Order().market_depth('zhfbtc', 'step0', 0)
    # Order().account_balance(1,'eos')
    # Order().order_all_cancel({"symbol": "zhfusdt"},0)