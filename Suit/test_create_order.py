
from Service.wbf_signature import Signature
from Service.config import Con
from Service import config
import pytest
import allure


@allure.feature('创建订单,/open/api/create_order')
class TestOpenApi(object):

    @allure.story('初始化全局变量')
    def setup_class(self):
        self.api_key = Con().environment(config.env_name)[0]
        self.secret_key = Con().environment(config.env_name)[1]
        self.host = Con().environment(config.env_name)[-2]
        self.tie = Con().now_time()
        print('测试用例开始执行!')

    @allure.story('下单参数校验-side-买卖方向')
    @pytest.mark.parametrize('side', ['', 'buy', 'Buy', 'sell', 'Sell'])
    def test_order_check_side(self, side):
        request_path = '/open/api/create_order'
        params = {
            "api_key": self.api_key,
            "time": self.tie, "side": side,
            "type": 1,
            "volume": 1,
            "price": 1,
            "symbol": config.symbol
        }
        result = Signature(self.secret_key).post_sign(config.types, params, request_path, self.host)
        print('下单response:{}'.format(result))
        if params['side'] == '':
            assert result['code'] == '100004'
        else:
            assert result['code'] == '5'

    @allure.story('下单参数校验-type-挂单类型')
    @pytest.mark.parametrize('type', [0, 4, 1.2, 'zhang', ''])
    def test_order_check_type(self, type):
        request_path = '/open/api/create_order'
        params = {
            "api_key": self.api_key,
            "time": self.tie, "side": "SELL",
            "type": type,
            "volume": 1,
            "price": 1,
            "symbol": config.symbol
        }
        result = Signature(self.secret_key).post_sign(config.types, params, request_path, self.host)
        print('下单response:{}'.format(result))
        if params['type'] == '':
            assert result['code'] == '100004'
        else:
            assert result['code'] == '5'

    @allure.story('下单参数校验-volume-购买数量')
    @pytest.mark.parametrize('volume', [0, 4000000, -1, 'zhang', ''])
    def test_order_check_volume(self, volume):
        request_path = '/open/api/create_order'
        params = {
            "api_key": self.api_key,
            "time": self.tie, "side": "SELL",
            "type": 1,
            "volume": volume,
            "price": 1,
            "symbol": config.symbol
        }
        result = Signature(self.secret_key).post_sign(config.types, params, request_path, self.host)
        print('下单response:{}'.format(result))
        if params['volume'] == '':
            assert result['code'] == '100004'
        else:
            assert result['code'] == '5'

    @allure.story('下单参数校验-price-价格')
    @pytest.mark.parametrize('price', [0, 4000000, -1, 'zhang', ''])
    def test_order_check_volume(self, price):
        request_path = '/open/api/create_order'
        params = {
            "api_key": self.api_key,
            "time": self.tie, "side": "SELL",
            "type": 1,
            "volume": 1,
            "price": price,
            "symbol": config.symbol
        }
        result = Signature(self.secret_key).post_sign(config.types, params, request_path, self.host)
        print('下单response:{}'.format(result))
        if params['price'] == '':
            assert result['code'] == '100005'
        elif params['price'] in [0, -1]:
            assert result['code'] == '10095'
        elif params['price'] == 4000000:
            assert result['code'] == '10094'
        else:
            assert result['code'] == '5'

    @allure.story('下单参数校验-price-type 下单类型,价格组合校验')
    @pytest.mark.parametrize('price,type', [(1, 2), ('', 2)])
    def test_order_check_volume(self, price, type):
        request_path = '/open/api/create_order'
        params = {
            "api_key": self.api_key,
            "time": self.tie, "side": "SELL",
            "type": type,
            "volume": 1,
            "price": price,
            "symbol": config.symbol
        }
        result = Signature(self.secret_key).post_sign(config.types, params, request_path, self.host)
        print('下单response:{}'.format(result))
        # if params['price'] == '':
        #     assert result['code'] == '100005'
        # elif params['price'] in [0, -1]:
        #     assert result['code'] == '10095'
        # elif params['price'] == 4000000:
        #     assert result['code'] == '10094'
        # else:
        #     assert result['code'] == '5'


if __name__ == '__main__':
    pytest.main(["-s", "test_account_balance.py"])