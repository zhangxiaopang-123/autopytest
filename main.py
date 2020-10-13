import pytest
import os
import allure
# # allure generate --clean D:/autopytest/report/xml/ -o D:/autopytest/report/html/
# d:
# cd D:\autopytest\
# python main.py
# allure generate --clean D:/report/xml/ -o D:/report/html/
# exit 0

if __name__ == "__main__":
    pytest.main(["-s", "-q", '--alluredir', 'D:/autopytest/report/xml'])
    # pytest.main(["-s", ""])