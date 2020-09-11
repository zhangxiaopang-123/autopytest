
from Service.wbf_signature import Signature
import time
from Service.config import environment
import pytest
import allure


@allure.feature('查询账户资产')
class TestOpenApi(object):

    def setup(self):
        self.api_key = environment(0)[0]
        self.secret_key = environment(0)[1]
        self.host = environment(0)[-2]
        self.tie = int(time.time())
        print('测试用例开始执行!')

    def teardown(self):
        print('测试用例执行结束!')

    @allure.story('用户资产查询成功')
    def test_balance(self):
        request_path = '/open/api/user/account'
        result = Signature(self.api_key, self.secret_key, self.tie).get_sign(request_path, self.host)
        print('查询资产成功response:{}'.format(result))
        assert result['msg'] == 'suc' and result['code'] == '0'

    @allure.story('用户资产查询失败')
    def test_fail(self):
        request_path = '/open/api/user/account'
        result = Signature(self.api_key, self.secret_key[:1], self.tie).get_sign(request_path, self.host)
        print('查询资产失败response:{}'.format(result))
        assert result['code'] == '100004'


if __name__ == '__main__':
    pytest.main(["-s", "test_account_balance.py"])