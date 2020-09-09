import time
import unittest
from Suit import test_account_balance
from Service import config
from Lib import HTML, email_new_report

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_account_balance.TestOpenApi)
    suit = unittest.TestSuite([suite])
    now = time.strftime("%Y%m%d%H%M")
    path = config.basedir + '\Report'
    # filename = path + '\Report_' + now + '.html'
    filename = path + '\Report.html'

    fp = open(filename, 'wb')
    runner = HTML.HTMLTestRunner(stream=fp,
                                           title=u'wbf接口自动化测试报告',
                                           # tester=u'张宏峰',
                                           description=u'测试用例执行情况如下,报告文件不可点击，详细信息请下载附件进行查看。'
                                           )
    runner.run(suit)
    fp.close()
    report = email_new_report.new_report(path)
    time.sleep(2)
    email_new_report.send_mail(report)




