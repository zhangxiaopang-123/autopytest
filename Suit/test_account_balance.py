
from Service.wbf_signature import Signature
import time
from Service.config import Con
from Service import config
import pytest
import allure


@allure.feature('查询账户资产,/open/api/user/account')
class TestOpenApi(object):

    def setup(self):
        self.api_key = Con().environment()[0]
        self.secret_key = Con().environment()[1]
        self.host = Con().environment()[-2]
        self.tie = Con().now_time()
        print('测试用例开始执行!')

    @allure.story('用户资产查询成功')
    def test_balance(self):
        request_path = '/open/api/user/account'
        params = {"api_key": self.api_key, "time": self.tie}
        result = Signature(self.secret_key).get_sign(config.types, params, request_path, self.host)
        print('查询资产成功response:{}'.format(result))
        assert result['msg'] == 'suc' and result['code'] == '0'

    @allure.story('用户资产查询失败')
    def test_fail(self):
        request_path = '/open/api/user/account'
        params = {"api_key": self.api_key, "time": self.tie}
        result = Signature(self.secret_key[:1]).get_sign(config.types, params, request_path, self.host)
        print('查询资产失败response:{}'.format(result))
        assert result['code'] == '100005'


if __name__ == '__main__':
    pytest.main(["-s", "test_account_balance.py"])