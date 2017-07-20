# coding: utf-8

import sys

if __name__ == "__main__":
    sys.path.append('..')
import time
import logging
import datetime
from selenium.common import exceptions as SeleniumExceptions
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from db import dbBasic
from EasyGoSpider import settings
from PIL import Image
from EasyGoSpider.yundama import get_captcha_res

reload(sys)
sys.setdefaultencoding('utf8')

TODAY = str(datetime.date.today())
ACCOUNT_FAIL_UPPER_LIMIT = 15
LoginURL = 'http://ui.ptlogin2.qq.com/cgi-bin/login?' \
           'appid=1600000601&style=9&s_url=http%3A%2F%2Fc.easygo.qq.com%2Feg_toc%2Fmap.html'
# ---------------------------------------------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
)
mongo_cli = dbBasic.MongoBasic()


# ---------------------------------------------------------------------------------------------------------------------


def update_time(item):
    item.update({'update_time': time.time()})


def init_cookies(myAccount):
    """    获取Cookies
    仅限新增账号初始化
    """
    for idx, elem in enumerate(myAccount):
        res = {}
        cookie = get_cookie_for_one_account(elem)
        res['account'] = elem
        res['cookie'] = cookie
        if cookie:
            logger.info(idx, elem, "init cookies done")
            update_time(res)
        if list(mongo_cli.cookies.find({"account": elem})):
            continue
        mongo_cli.cookies.insert(res)


def get_cookie_for_one_account(elem):
    account = elem['no']
    password = elem['psw']
    logger.info("Fetching cookie for %s" % account)

    for i in xrange(3):
        logger.info("Trying %s time%s..." % (i + 1, "s" if i else ''))
        try:
            browser = webdriver.PhantomJS(desired_capabilities=dcap)
            browser.get(LoginURL)
            time.sleep(3)

            username = browser.find_element_by_id("u")
            username.clear()
            username.send_keys(account)
            psd = browser.find_element_by_id("p")
            psd.clear()
            psd.send_keys(password)
            commit = browser.find_element_by_id("go")
            commit.click()
            time.sleep(5)

            if "宜出行" in browser.title:
                return after_smoothly_login(browser)
            elif "手机统一登录" in browser.title:
                browser.switch_to.frame(browser.find_element_by_xpath(r'//*[@id="new_vcode"]/iframe[2]'))
                time.sleep(2)
                img_path = './verify_code.png'
                save_verify_img = browser.find_element_by_xpath(r'//*[@id="cap_que_img"]').screenshot(img_path)
                with Image.open(img_path) as f:
                    x, y = 65, 89
                    w, h = 132, 53
                    f.crop((x, y, x + w, y + h)).save(img_path)
                if save_verify_img:
                    verify_res = recogniz_vcode(img_path)
                    verify_aera = browser.find_element_by_xpath(r'//*[@id="cap_input"]')  # 65, 89, 132, 53
                    verify_aera.clear()
                    verify_aera.send_keys(verify_res)
                    browser.find_element_by_xpath(r'//span[@id="verify_btn"]').click()
                    time.sleep(3)
                    if "宜出行" in browser.title:
                        return after_smoothly_login(browser)
                    else:
                        mongo_cli.cookies.find_one_and_update({"account": elem}, {"$inc": {"AuthFailed": 1}})

        except SeleniumExceptions.NoSuchElementException, e:
            logger.debug(e)
        except Exception, e:
            logger.debug(e)
        finally:
            try:
                browser.quit()
            except:
                pass
    logger.warning("Get Cookie Failed: %s!" % account)
    return {}


def recogniz_vcode(img_path):
    """     识别验证码
    """
    if settings.CAPTCHA_RECOGNIZ == 1:  # manually recognize captcha
        logger.debug("请找到 %s " % img_path)
        return raw_input("手动在此处输入验证码：\n")
    elif settings.CAPTCHA_RECOGNIZ == 2:  # auto via yundama
        return get_captcha_res(img_path)


def after_smoothly_login(browser):
    """     成功登录之后
    """
    cookie = {}
    for elem in browser.get_cookies():
        cookie[elem["name"]] = elem["value"]
    if len(cookie) > 0:
        logger.info("...got a new cookie")
        return cookie


def fetch_cookies(ignored_cookies):
    """    fetch existed cookies from mongo
    """
    if settings.REFRESH_COOKIES:
        for dct in mongo_cli.cookies.find({}):
            try:
                assert dct.get('FailedDate') != TODAY  # 今日访问次数过多
                assert dct.get("AuthFailed") < ACCOUNT_FAIL_UPPER_LIMIT  # 可能被禁
                assert dct.get("cookie") not in ignored_cookies
                assert dct.get("update_time") is None or time.time() - dct.get("update_time") > settings.COOKIE_INTERVAL
                refresh_cookie(dct)
            except AssertionError:
                continue
    return [i['cookie'] for i in mongo_cli.cookies.find({})
            if i['cookie']
            and (i.get('FailedDate') != TODAY)
            and (i.get("AuthFailed") < ACCOUNT_FAIL_UPPER_LIMIT)]


def refresh_cookie(dct):
    """    update cookie which is no longer available
    """
    new_cookie = get_cookie_for_one_account(dct.get('account'))
    update_part = {'cookie': new_cookie}
    update_time(update_part)
    mongo_cli.cookies.find_one_and_update({'_id': dct['_id']},
                                          {'$set': update_part})


def try_to_get_enough_cookies():
    cookies = []
    for i in xrange(3):
        cookies = fetch_cookies(cookies)
        if len(cookies) >= 3:
            return cookies
        if i < 2:
            logger.info("Find %s. Not enough. Trying again..." % i)
    return cookies


if __name__ == '__main__':
    # try_to_get_enough_cookies(1)
    myAccount = []
    for line in ''' '''.split():
        no, psw = line.split('----')
        myAccount.append({'no': no, 'psw': psw})
    print myAccount.__repr__()
    init_cookies(myAccount)
