
from Service.wbf_signature import Signature
import time
from Service.config import Con
from Service import config
from Service import open_api_service
from Service import sqlmethods
import pytest
import allure


@allure.feature('清算验证,/open/api/create_order')
class TestOpenApiClearing(object):

    def setup(self):
        open_api_service.Order().cancel_all(config.types)  # 撤销盘口所有订单
        self.api_key = Con().environment()[0]
        self.secret_key = Con().environment()[1]
        self.host = Con().environment()[-2]
        self.tie = Con().now_time()
        self.db_host = Con().sql()[0]
        self.db_user = Con().sql()[1]
        self.db_password = Con().sql()[2]
        self.db_port = Con().sql()[3]
        self.db_database = Con().sql()[4]
        self.request_path = '/open/api/create_order'
        self.p = {
            "api_key": self.api_key,
            "time": self.tie,
            "symbol": config.symbol
        }
        self.xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期初正常余额
        self.xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期初冻结余额
        self.usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期初正常余额
        self.usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期初冻结余额
        print("xp期初正常余额:{};xp期初冻结余额:{};usdt期初正常余额:{};usdt期初冻结余额:{}".format(
            self.xp_normal, self.xp_locked, self.usd_normal, self.usd_locked))
        # print('测试用例开始执行!')

    @allure.story('一对一,成交价等于下单价,市价、限价订单用例执行开始！')
    @allure.story('限价买单完全挂单')
    def test_buy_limit(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)

        # print('限价买单-币对:{},响应结果:{}'.format(config.symbol, result))
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        assert self.xp_normal == xp_normal and self.xp_locked == xp_locked  # 买单挂单 xp余额无变化
        # 期初正常usd - 买入价*买入量 = 期末正常usd
        # 期初冻结usd + 买入价*买入量 = 期末冻结usd
        assert (float(self.usd_normal) - float(float(params["price"]) * float(params["volume"]))) == float(usd_normal)
        assert (float(self.usd_locked) + float(float(params["price"]) * float(params["volume"]))) == float(usd_locked)
        # 期末冻结usd + 期末正常usd = 期初usd
        assert (float(usd_locked) + float(usd_normal)) == float(self.usd_normal)

        sql = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 1;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sql)
        # print(rq)
        assert result['data']['order_id'] == rq[0][0] and rq[0][1] == 0 and rq[0][2] == 'BUY' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('限价卖单完全挂单')
    def test_sell_limit(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        # print('限价买单-币对:{},响应结果:{}'.format(config.symbol, result))
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        assert self.usd_normal == usd_normal and self.usd_locked == usd_locked  # 卖单挂单 usd余额无变化
        # 期初正常xp - 卖出量 = 期末正常xp
        # 期初冻结xp + 卖出量 = 期末冻结xp
        assert (float(self.xp_normal) - float(params["volume"])) == float(xp_normal)
        assert (float(self.xp_locked) + float(params["volume"])) == float(xp_locked)

        # 期末冻结xp + 期末正常xp = 期初xp
        assert (float(xp_locked) + float(xp_normal)) == float(self.xp_normal)

        sql = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 1;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sql)
        # print(rq)
        assert result['data']['order_id'] == rq[0][0] and rq[0][1] == 0 and rq[0][2] == 'SELL' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('限价买单完全撤单')
    def test_buy_limit_cancel(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        time.sleep(1)
        open_api_service.Order().cancel_all(config.types)
        # print('限价买单-币对:{},响应结果:{}'.format(config.symbol, result))
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        assert self.xp_normal == xp_normal and self.xp_locked == xp_locked  # 限价买单撤单 xp余额无变化
        assert self.usd_normal == usd_normal and self.usd_locked == usd_locked  # 限价买单撤单 usd余额无变化
        sql = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 1;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sql)
        # print(rq)
        assert result['data']['order_id'] == rq[0][0] and rq[0][1] == 4 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('限价卖单完全撤单')
    def test_sell_limit_cancel(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        # print('限价买单-币对:{},响应结果:{}'.format(config.symbol, result))
        # 执行撤单
        time.sleep(1)
        open_api_service.Order().cancel_all(config.types)
        # xp 期末正常余额
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]
        # xp 期末冻结余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]
        # usdt 期末正常余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]
        # usdt 期末冻结余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]
        # 限价卖单撤单 usd余额无变化
        assert self.usd_normal == usd_normal and self.usd_locked == usd_locked
        # 限价卖单撤单 xp余额无变化
        assert self.xp_normal == xp_normal and self.xp_locked == xp_locked
        sql = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 1;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sql)
        # print(rq)
        assert result['data']['order_id'] == rq[0][0] and rq[0][1] == 4 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('限价买单部分成交')
    def test_buy_limit_part_filled(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 1,
            "volume": 0.9,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(0.9) * float(0.1)) - float(float(params["price"]) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked) + float(float(params["price"]) * float(0.1)), 4) == round(float(usd_locked), 4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(0.9) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 3 and rq[-1][2] == 'BUY' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('限价买单部分成交后继续成交达到完全成交')
    def test_buy_limit_part_filled_all(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 1,
            "volume": 0.9,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单1
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        sell = {
            "side": "SELL",
            "type": 1,
            "volume": 0.1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        sell.update(self.p)
        # 下卖单2
        r = Signature(self.secret_key).post_sign(config.types, sell, self.request_path, self.host)
        print("sell-{}".format(r))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 3;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'BUY' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[1][0] and rq[1][1] == 2 and rq[1][2] == 'SELL' and rq[1][3] == 1
        assert r['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('限价买单完全成交')
    def test_buy_limit_filled(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                                                                      4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'BUY' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('限价买单部分成交撤单')
    def test_buy_limit_part_filled_cancel(self):

        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 1,
            "volume": 0.9,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))
        open_api_service.Order().cancel_all(config.types)
        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(0.9) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked), 4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(0.9) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 4 and rq[-1][2] == 'BUY' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('限价卖单部分成交')
    def test_sell_limit_part_filled(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 0.9,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(0.9) * float(0.1)), 4)) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                                                                      4)
        # 期初正常xp - 卖出量*手续费率 - （卖出量-买入量） = 期末正常xp
        assert round(float(self.xp_normal) - float(float(0.9) * float(0.1)) - float(0.1), 4) == round(float(xp_normal), 4)
        # 期初冻结xp + (卖出量-买入量)  = 期末冻结xp
        assert (round(float(self.xp_locked) + float(0.1), 4)) == round(float(xp_locked), 4)
        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 3 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('限价卖单部分成交后继续成交达到完全成交')
    def test_sell_limit_part_filled_all(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 0.9,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下买单1
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        buy = {
            "side": "BUY",
            "type": 1,
            "volume": 0.1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        buy.update(self.p)
        # 下买单2
        r = Signature(self.secret_key).post_sign(config.types, buy, self.request_path, self.host)
        print("sell-{}".format(r))

        time.sleep(7)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 3;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[1][0] and rq[1][1] == 2 and rq[1][2] == 'BUY' and rq[1][3] == 1
        assert r['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('限价卖单完全成交')
    def test_sell_limit_filled(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('限价卖单部分成交撤单')
    def test_sell_limit_part_filled_cancel(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 0.9,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))
        open_api_service.Order().cancel_all(config.types)
        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(0.9) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked), 4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(0.9) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 4 and rq[-1][2] == 'SELL' and rq[0][3] == 1

    @allure.story('市价买单自动撤单,盘口无数据')
    def test_buy_market(self):
        params = {
            "side": "BUY",
            "type": 2,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        # print('限价买单-币对:{},响应结果:{}'.format(config.symbol, result))
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        assert self.xp_normal == xp_normal and self.xp_locked == xp_locked  # 市价自动撤单 xp余额无变化
        assert self.usd_normal == usd_normal and self.usd_locked == usd_locked  # 市价自动撤单 usd余额无变化
        sql = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 1;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sql)
        # print(rq)
        assert result['data']['order_id'] == rq[0][0] and rq[0][1] == 4 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('市价卖单自动撤单,盘口无数据')
    def test_sell_market(self):
        params = {
            "side": "SELL",
            "type": 2,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        # print('限价买单-币对:{},响应结果:{}'.format(config.symbol, result))
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        assert float(self.usd_normal) == float(usd_normal) and float(self.usd_locked) == float(
            usd_locked)  # 卖单市价自动撤单 usd余额无变化
        assert float(self.xp_normal) == float(xp_normal) and float(self.xp_locked) == float(xp_locked)  # 市价自动撤单 xp余额无变化
        sql = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 1;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sql)
        # print(rq)
        assert result['data']['order_id'] == rq[0][0] and rq[0][1] == 4 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('市价买单部分成交自动撤单')
    def test_buy_market_part_filled_cancel(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 2,
            "volume": round(float(params["volume"]*params["price"]) + 1, 4),
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下市价买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率  = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                                                                      4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('市价买单完全成交')
    def test_buy_market_filled(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 2,
            "volume": round(float(params["volume"]*params["price"]), 4),
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('市价买单超过风险率自动撤单,目前撮合默认风险率为0.2,代码写法是默认固定值')
    def test_buy_market_risk_cancel(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 1,
            "volume": float(params["volume"]),
            "price": round(open_api_service.Order().lastprice(config.symbol) * 0.2 + float(params["price"]), 4),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        buy = {
            "side": "BUY",
            "type": 2,
            "volume": round((float(params["volume"] + float(data["volume"])) * params["price"]), 4),
        }
        buy.update(self.p)
        # 下买单
        r = Signature(self.secret_key).post_sign(config.types, buy, self.request_path, self.host)
        print("sell-{}".format(r))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 卖出量*手续费率 - data["volume"] = 期末正常xp
        assert round(
            float(self.xp_normal) - float(float(1) * float(0.1)) - float(data["volume"]), 4) == round(float(xp_normal), 4)
        # 期初冻结xp + data["volume"] = 期末冻结xp
        assert round(
            float(self.xp_locked), 4) + float(data["volume"]) == round(float(xp_locked), 4)
        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 3;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[1][0] and rq[1][1] == 0 and rq[1][2] == 'SELL' and rq[0][3] == 1
        assert r['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('市价卖单部分成交自动撤单')
    def test_sell_market_part_filled_cancel(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 2,
            "volume": float(params["volume"]) + 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*买入量*手续费率 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 买入量*手续费率 - （卖出量-买入量） = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)

        # 期初冻结xp   = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)
        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'BUY' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('一对一,成交价等于下单价,市价、限价订单用例执行结束！')
    @allure.story('市价卖单完全成交')
    def test_sell_market_filled(self):
        params = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "SELL",
            "type": 1,
            "volume": params["volume"],
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*买入量*手续费率  = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked),
                                                         4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'BUY' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('一对一,限价买单成交价小于下单价--start!')
    @allure.story('限价买单部分成交')
    def test_buy_limit_part_filled_less_market(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 2,
            "price": (open_api_service.Order().lastprice(config.symbol) + 1),
        }
        data.update(self.p)
        # 下买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(1) * float(0.1)) - float(float(data["price"]) * (
                float(data["volume"]) - float(params["volume"]))), 4)) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked) + float(data["price"]) * (
                float(data["volume"]) - float(params["volume"])), 4) == round(float(usd_locked), 4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(params["volume"]) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 3 and rq[0][2] == 'BUY' and rq[0][3] == 1
        open_api_service.Order().cancel_all(config.types)

    @allure.story('限价买单部分成交后继续成交达到完全成交')
    def test_buy_limit_part_filled_all_less_market(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 2,
            "price": open_api_service.Order().lastprice(config.symbol)+1,
        }
        data.update(self.p)
        # 下买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        sell = {
            "side": "SELL",
            "type": 1,
            "volume": float(data["volume"] - params["volume"]),
            "price": float(data["price"]),
        }
        sell.update(self.p)
        # 下卖单
        r = Signature(self.secret_key).post_sign(config.types, sell, self.request_path, self.host)
        print("sell-{}".format(r))

        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(float(params["price"]) * float(
            params["volume"]) * float(0.1)) - float(
            float(sell["price"]) * float(sell["volume"]) * float(0.1)), 4)) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked), 4)

        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(float(self.xp_normal) - float(float(params["volume"]) * float(0.1)) - float(
            float(sell["volume"]) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert round(
            float(self.xp_locked), 4) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 3;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[1][0] and rq[1][1] == 2 and rq[1][2] == 'BUY' and rq[1][3] == 1
        assert r['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'SELL' and rq[0][3] == 1

    @allure.story('限价买单完全成交')
    def test_buy_limit_filled_less_market(self):
        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下卖单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下买单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))

        time.sleep(7)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(params["volume"]) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
        assert round(
            float(self.usd_locked), 4) == round(float(usd_locked), 4)

        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(
            float(self.xp_normal) - float(float(params["volume"]) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1

    @allure.story('一对一,限价买单成交价小于下单价--end!')
    @allure.story('限价买单部分成交撤单')
    def test_buy_limit_part_filled_cancel_less_market(self):

        params = {
            "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        params.update(self.p)
        # 下买单
        result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
        print("buy-{}".format(result))
        data = {
            "side": "BUY",
            "type": 1,
            "volume": 2,
            "price": open_api_service.Order().lastprice(config.symbol),
        }
        data.update(self.p)
        # 下卖单
        res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
        print("sell-{}".format(res))
        open_api_service.Order().cancel_all(config.types)
        time.sleep(10)
        xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
        xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
        usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
        usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
        print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
            xp_normal, xp_locked, usd_normal, usd_locked))

        # 期初正常usd - 成交价*卖出量*手续费率 = 期末正常usd
        assert (round(float(self.usd_normal) - float(
            float(params["price"]) * float(params["volume"]) * float(0.1)), 4)
                ) == round(float(usd_normal), 4)
        # 期初冻结usd  = 期末冻结usd
        assert round(float(self.usd_locked), 4) == round(float(usd_locked), 4)
        # 期初正常xp - 卖出量*手续费率 = 期末正常xp
        assert round(
            float(self.xp_normal) - float(float(params["volume"]) * float(0.1)), 4) == round(float(xp_normal), 4)
        # 期初冻结xp  = 期末冻结xp
        assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)

        sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
            config.symbol, config.user_id)  # 查询订单
        rq = sqlmethods.SQL(
            self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
        print(rq)
        assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
        assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 4 and rq[0][2] == 'BUY' and rq[0][3] == 1








    # @allure.story('一对一,限价卖单成交价大于下单价--start!')
    # @allure.story('限价卖单部分成交')
    # def test_sell_limit_part_filled_more_market(self):
    #     params = {
    #         "side": "SELL",
    #         "type": 1,
    #         "volume": 1,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     params.update(self.p)
    #     # 下卖单
    #     result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
    #     print("buy-{}".format(result))
    #     data = {
    #         "side": "BUY",
    #         "type": 1,
    #         "volume": 0.9,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     data.update(self.p)
    #     # 下买单
    #     res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
    #     print("sell-{}".format(res))
    #
    #     time.sleep(10)
    #     xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
    #     xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
    #     usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
    #     usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
    #     print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
    #         xp_normal, xp_locked, usd_normal, usd_locked))
    #
    #     # 期初正常usd - 成交价*卖出量*手续费率 = 期末正常usd
    #     assert (round(float(self.usd_normal) - float(
    #         float(params["price"]) * float(0.9) * float(0.1)), 4)) == round(float(usd_normal), 4)
    #     # 期初冻结usd  = 期末冻结usd
    #     assert round(float(self.usd_locked), 4) == round(float(usd_locked),
    #                                                      4)
    #     # 期初正常xp - 卖出量*手续费率 - （卖出量-买入量） = 期末正常xp
    #     assert round(float(self.xp_normal) - float(float(0.9) * float(0.1)) - float(0.1), 4) == round(float(xp_normal),
    #                                                                                                   4)
    #     # 期初冻结xp + (卖出量-买入量)  = 期末冻结xp
    #     assert (round(float(self.xp_locked) + float(0.1), 4)) == round(float(xp_locked), 4)
    #     sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
    #         config.symbol, config.user_id)  # 查询订单
    #     rq = sqlmethods.SQL(
    #         self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
    #     print(rq)
    #     assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 3 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
    #     assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
    #     open_api_service.Order().cancel_all(config.types)
    #
    # @allure.story('限价卖单部分成交后继续成交达到完全成交')
    # def test_sell_limit_part_filled_all_more_market(self):
    #     params = {
    #         "side": "SELL",
    #         "type": 1,
    #         "volume": 1,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     params.update(self.p)
    #     # 下卖单
    #     result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
    #     print("buy-{}".format(result))
    #     data = {
    #         "side": "BUY",
    #         "type": 1,
    #         "volume": 0.9,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     data.update(self.p)
    #     # 下买单1
    #     res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
    #     print("sell-{}".format(res))
    #
    #     buy = {
    #         "side": "BUY",
    #         "type": 1,
    #         "volume": 0.1,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     buy.update(self.p)
    #     # 下买单2
    #     r = Signature(self.secret_key).post_sign(config.types, buy, self.request_path, self.host)
    #     print("sell-{}".format(r))
    #
    #     time.sleep(7)
    #     xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
    #     xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
    #     usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
    #     usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
    #     print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
    #         xp_normal, xp_locked, usd_normal, usd_locked))
    #
    #     # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
    #     assert (round(float(self.usd_normal) - float(
    #         float(params["price"]) * float(1) * float(0.1)), 4)
    #             ) == round(float(usd_normal), 4)
    #     # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
    #     assert round(float(self.usd_locked), 4) == round(float(usd_locked),
    #                                                      4)
    #     # 期初正常xp - 卖出量*手续费率 = 期末正常xp
    #     assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
    #     # 期初冻结xp  = 期末冻结xp
    #     assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)
    #
    #     sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 3;" % (
    #         config.symbol, config.user_id)  # 查询订单
    #     rq = sqlmethods.SQL(
    #         self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
    #     print(rq)
    #     assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
    #     assert res['data']['order_id'] == rq[1][0] and rq[1][1] == 2 and rq[1][2] == 'BUY' and rq[1][3] == 1
    #     assert r['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
    #
    # @allure.story('限价卖单完全成交')
    # def test_sell_limit_filled_more_market(self):
    #     params = {
    #         "side": "SELL",
    #         "type": 1,
    #         "volume": 1,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     params.update(self.p)
    #     # 下买单
    #     result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
    #     print("buy-{}".format(result))
    #     data = {
    #         "side": "BUY",
    #         "type": 1,
    #         "volume": 1,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     data.update(self.p)
    #     # 下卖单
    #     res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
    #     print("sell-{}".format(res))
    #
    #     time.sleep(10)
    #     xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
    #     xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
    #     usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
    #     usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
    #     print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
    #         xp_normal, xp_locked, usd_normal, usd_locked))
    #
    #     # 期初正常usd - 成交价*卖出量*手续费率 - （买入量-卖出量）*买入价 = 期末正常usd
    #     assert (round(float(self.usd_normal) - float(
    #         float(params["price"]) * float(1) * float(0.1)), 4)
    #             ) == round(float(usd_normal), 4)
    #     # 期初冻结usd + （买入量-卖出量）*买入价 = 期末冻结usd
    #     assert round(float(self.usd_locked), 4) == round(float(usd_locked),
    #                                                      4)
    #     # 期初正常xp - 卖出量*手续费率 = 期末正常xp
    #     assert round(float(self.xp_normal) - float(float(1) * float(0.1)), 4) == round(float(xp_normal), 4)
    #     # 期初冻结xp  = 期末冻结xp
    #     assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)
    #
    #     sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
    #         config.symbol, config.user_id)  # 查询订单
    #     rq = sqlmethods.SQL(
    #         self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
    #     print(rq)
    #     assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 2 and rq[-1][2] == 'SELL' and rq[-1][3] == 1
    #     assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
    #
    # @allure.story('一对一,限价卖单成交价大于下单价--end!')
    # @allure.story('限价卖单部分成交撤单')
    # def test_sell_limit_part_filled_cancel_more_market(self):
    #     params = {
    #         "side": "SELL",
    #         "type": 1,
    #         "volume": 1,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     params.update(self.p)
    #     # 下卖单
    #     result = Signature(self.secret_key).post_sign(config.types, params, self.request_path, self.host)
    #     print("buy-{}".format(result))
    #     data = {
    #         "side": "BUY",
    #         "type": 1,
    #         "volume": 0.9,
    #         "price": open_api_service.Order().lastprice(config.symbol),
    #     }
    #     data.update(self.p)
    #     # 下买单
    #     res = Signature(self.secret_key).post_sign(config.types, data, self.request_path, self.host)
    #     print("sell-{}".format(res))
    #     open_api_service.Order().cancel_all(config.types)
    #     time.sleep(10)
    #     xp_normal = open_api_service.Order().account_balance(config.types, config.currency[0])[0]  # xp 期末正常余额
    #     xp_locked = open_api_service.Order().account_balance(config.types, config.currency[0])[1]  # xp 期末冻结余额
    #     usd_normal = open_api_service.Order().account_balance(config.types, config.currency[1])[0]  # usdt 期末正常余额
    #     usd_locked = open_api_service.Order().account_balance(config.types, config.currency[1])[1]  # usdt 期末冻结余额
    #     print("xp期末正常余额:{};xp期末冻结余额:{};usdt期末正常余额:{};usdt期末冻结余额:{}".format(
    #         xp_normal, xp_locked, usd_normal, usd_locked))
    #
    #     # 期初正常usd - 成交价*卖出量*手续费率 = 期末正常usd
    #     assert (round(float(self.usd_normal) - float(
    #         float(params["price"]) * float(0.9) * float(0.1)), 4)
    #             ) == round(float(usd_normal), 4)
    #     # 期初冻结usd  = 期末冻结usd
    #     assert round(float(self.usd_locked), 4) == round(float(usd_locked), 4)
    #     # 期初正常xp - 卖出量*手续费率 = 期末正常xp
    #     assert round(float(self.xp_normal) - float(float(0.9) * float(0.1)), 4) == round(float(xp_normal), 4)
    #     # 期初冻结xp  = 期末冻结xp
    #     assert (round(float(self.xp_locked), 4)) == round(float(xp_locked), 4)
    #
    #     sl = "select id,status,side,in_seq from  ex_order_%s where user_id = %d order by id desc limit 2;" % (
    #         config.symbol, config.user_id)  # 查询订单
    #     rq = sqlmethods.SQL(
    #         self.db_host, self.db_user, self.db_password, self.db_port, self.db_database).sql_select(sl)
    #     print(rq)
    #     assert res['data']['order_id'] == rq[0][0] and rq[0][1] == 2 and rq[0][2] == 'BUY' and rq[0][3] == 1
    #     assert result['data']['order_id'] == rq[-1][0] and rq[-1][1] == 4 and rq[-1][2] == 'SELL' and rq[0][3] == 1

















if __name__ == '__main__':
    pytest.main(["-s", "test_clearing.py"])