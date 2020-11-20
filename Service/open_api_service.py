from Service import wbf_signature
import requests
from Service.config import Con
from Service import config

api_key = Con().environment()[0]
secret_key = Con().environment()[1]
host = Con().environment()[-2]


class Order:

    def market_depth(self, sym, typ):
        """
        获取市场买卖盘
        :return:
        """
        request_path = '/open/api/market_dept'
        url = host + request_path
        params = {"symbol": sym, "type": typ}
        try:
            res = requests.get(url=url, params=params)
            if res.status_code == 200:
                r = res.json()
                Con().info_log(params, url, r)
                return r
        except Exception as e:
            # print('error：{}'.format(e))
            Con().error_log(params, url, e)

    def lastprice(self, symbol):
        """
        获取最新成交价
        :param symbol:
        :return:
        """
        url = host + '/open/api/market'
        params = {"symbol": symbol}
        try:
            result = requests.get(url, params=params)
            Con().info_log(params, url, result)
            if result.status_code == 200:
                last_price = result.json()['data'][symbol]
                Con().info_log(params, url, last_price)
                return last_price
        except Exception as e:
            print("error:{}".format(e))
            Con().error_log(params, url, e)

    def account_balance(self, types, currency):
        """
        查询账户资产
        :return:
        """
        p = {"api_key": api_key, "time": Con().now_time()}
        request_path = '/open/api/user/account'
        result = wbf_signature.Signature(secret_key).get_sign(types, p, request_path, host)
        # print('查询资产响应:{}'.format(result))
        coin = result['data']['coin_list']
        for i in range(0, len(coin)):
            if coin[i]['coin'] == currency:
                Con().info_log(currency, coin[i]['normal'], coin[i]['locked'])
                print('查询资产:{},{}'.format(coin[i]['normal'], coin[i]['locked']))
                return coin[i]['normal'], coin[i]['locked']

    def unfilled_order(self, types, p):
        """
        查询全部委托单
        :param types:
        :return:
        """
        # print(p)
        request_path = '/open/api/v2/all_order'
        result = wbf_signature.Signature(secret_key).get_sign(types, p, request_path, host)
        print('查询全部委托单:{}'.format(result))

    def all_record_order(self, types, p):
        """
        查询全部成交记录
        :param types:
        :return:
        """
        request_path = '/open/api/all_trade'
        result = wbf_signature.Signature(secret_key).get_sign(types, p, request_path, host)
        print('查询全部成交记录:{}'.format(result))

    def order_cancel(self, types, p):
        """
        撤销订单
        :param p:
        :return:
        """
        request_path = '/open/api/cancel_order'
        result = wbf_signature.Signature(secret_key).post_sign(types, p, request_path, host)
        print('撤销订单:{}'.format(result))

    def cancel_all(self, types):
        """
        撤销全部订单
        :param p:
        :return:
        """
        request_path = '/open/api/cancel_order_all'
        params = {
            "api_key": api_key,
            "time": Con().now_time(),
            "symbol": config.symbol
        }
        result = wbf_signature.Signature(secret_key).post_sign(types, params, request_path, host)
        print('撤销全部订单:{}'.format(result))

    def order_place(self, types, p):
        """
        创建订单
        :param p:
        :return:
        """
        request_path = '/open/api/create_order'
        result = wbf_signature.Signature(secret_key).post_sign(types, p, request_path, host)
        print('创建订单:{}'.format(result))

    def order_place_all(self, types, p):
        """
        批量创建订单
        :param p:
        :return:
        """
        request_path = '/open/api/mass_replace'
        result = wbf_signature.Signature(secret_key).post_sign(types, p, request_path, host)
        print('批量创建订单:{}'.format(result))

    def order_place_all_v2(self, types, p):
        """
        批量创建订单
        :param p:
        :return:
        """
        request_path = '/open/api/mass_replaceV2'
        result = wbf_signature.Signature(secret_key).post_sign(types, p, request_path, host)
        print('批量创建订单:{}'.format(result))

    def unfilled_order_v2(self, types):
        """
        查询当前委托单
        :param types:
        :return:
        """
        params = {
            "api_key": api_key,
            "time": Con().now_time(),
            "symbol": config.symbol
        }
        request_path = '/open/api/v2/new_order'
        result = wbf_signature.Signature(secret_key).get_sign(types, params, request_path, host)
        print('查询当前委托单:{}'.format(result))

    def order_detail(self, types, p):
        """
        订单详情
        :return:
        """
        request_path = '/open/api/order_info'
        result = wbf_signature.Signature(secret_key).get_sign(types, p, request_path, host)
        print('查询订单详情:{}'.format(result))


if __name__ == '__main__':

    Order().account_balance(config.types, config.currency[1])[0]
    # Order().lastprice('xpusdt')
    # Order().account_balance('old', 'eos')  # 账户资产新老验签方式验证
    # p = {
    #         "api_key": api_key,
    #         "time": Con().now_time(),
    #         "symbol": config.symbol,
    #         "startDate": '2020-08-30 12:21:34',  # 开始时间;yyyy-MM-dd HH:mm:ss;选填
    #         "endDate": '2020-09-30 12:21:34',  # 结束时间;选填;yyyy-MM-dd HH:mm:ss
    #         "pageSize": 1,  # 页面大小;选填
    #         "page": 1,  # 页面;选填
    #         # "sort": 1,  # 顺序 1倒叙;2正序;选填
    #     }
    # Order().unfilled_order('new', p)  # 查询当前所有委托订单
    # Order().all_record_order('new', p)  # 获取全部成交记录
    # p = {
    #     "order_id": 4,
    #     "api_key": api_key,
    #     "time": Con().now_time(),
    #     "symbol": config.symbol,
    # }
    # Order().order_cancel('new', p)  # 撤销订单
    #
    # p = {
    #     "api_key": api_key,
    #     "time": Con().now_time(),
    #     "symbol": config.symbol,
    # }
    # Order().cancel_all('new', p)  # 撤销全部订单
    #
    # p = {"side": "BUY", "type": 1, "volume": 1, "symbol": config.symbol, "price": 1, "api_key": api_key,
    #      "time": Con().now_time()}
    # Order().order_place('old', p)  # 创建订单

    # p = {
    #     "symbol": config.symbol, "mass_place":
    #     str([{"side": "BUY", "type": 1, "volume": 1, "symbol": config.symbol, "price": 1}]),
    #     "api_key": api_key, "time": Con().now_time(), "mass_cancel": str([60, 61, 62])
    #           }
    # Order().order_place_all('new', p)  # 批量创建订单
    # Order().order_place_all_v2('new', p)  # 批量创建订单v2
    # p = {
    #         "api_key": api_key,
    #         "time": Con().now_time(),
    #         "symbol": config.symbol,
    #         "pageSize": 1,  # 页面大小;选填
    #         "page": 1,  # 页面;选填
    #     }
    # Order().unfilled_order_v2('old')  # 查询当前委托单
    # p = {
    #     "api_key": api_key,
    #     "time": Con().now_time(),
    #     "symbol": config.symbol,
    #     "order_id": 66,
    # }
    #
    # Order().order_detail('old', p)  # 查询订单详情
    #

