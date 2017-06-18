# coding: utf-8

import sys
import time
from selenium.common import exceptions as SeleniumExceptions
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from db import dbBasic
from EasyGoSpider import settings
import datetime
from PIL import Image
from EasyGoSpider.yundama import get_captcha_res

today = str(datetime.date.today())
IDENTITY = settings.CAPTCHA_RECOGNIZ
reload(sys)
sys.setdefaultencoding('utf8')
dcap = dict(DesiredCapabilities.PHANTOMJS)  # PhantomJS需要使用老版手机的user-agent，不然验证码会无法通过
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
)

mongo_cli = dbBasic.MongoBasic()
loginURL = 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=1600000601&style=9&s_url=http%3A%2F%2Fc.easygo.qq.com%2Feg_toc%2Fmap.html'

def initCookies(myAccount):
    """
    获取Cookies
    仅限初始化
    """
    for idx, elem in enumerate(myAccount):
        res = {}
        cookie = getCookie(elem)
        # res['_id'] = idx
        res['account'] = elem
        res['cookie'] = cookie
        if cookie:
            print idx, elem, "init cookies done"
        if list(mongo_cli.cookies.find({"account": elem})):
            continue
        mongo_cli.cookies.insert(res)

def getCookie(elem):

    account = elem['no']
    password = elem['psw']
    print "Fetching cookie for", account

    for i in xrange(3):
        print "Trying %s time%s..." % (i+1, "s" if i else '')
        try:
            browser = webdriver.PhantomJS(desired_capabilities=dcap)
            browser.get(loginURL)
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
                    f.crop((x, y, x+w, y+h)).save(img_path)
                if save_verify_img:
                    verify_res = recogniz_vcode(img_path)
                    verify_aera = browser.find_element_by_xpath(r'//*[@id="cap_input"]') # 65, 89, 132, 53
                    verify_aera.clear()
                    verify_aera.send_keys(verify_res)
                    browser.find_element_by_xpath(r'//span[@id="verify_btn"]').click()
                    time.sleep(3)
                    if "宜出行" in browser.title:
                        return after_smoothly_login(browser)
                    else:
                        mongo_cli.cookies.find_one_and_update({"account": elem}, {"$inc": {"AuthFailed": 1}})

        except SeleniumExceptions.NoSuchElementException, e:
            print e.__class__.__name__, e
        except Exception, e:
            print e.__class__.__name__, e
        finally:
            try:
                browser.quit()
            except:
                pass
    print "Get Cookie Failed: %s!" % account
    return {}


def recogniz_vcode(img_path):
    if IDENTITY == 1:  # manually recognize captcha
        print "请找到 %s " % img_path
        return raw_input("手动在此处输入验证码：\n")
    elif IDENTITY == 2:  # auto via yundama
        return get_captcha_res(img_path)


def after_smoothly_login(browser):
    cookie = {}
    for elem in browser.get_cookies():
        cookie[elem["name"]] = elem["value"]
    if len(cookie) > 0:
        print "...got a new cookie"
        return cookie


def fetchCookies(CUSTOM_REFRESH=0):
    """
    fetch existed cookies from mongo
    """
    if settings.REFRESH_TOKENS or CUSTOM_REFRESH:
        for dct in mongo_cli.cookies.find({}):
            if dct.get('FailedDate') != today and dct.get("AuthFailed") < 10:
                refresh_cookie(dct)
    return [i['cookie'] for i in mongo_cli.cookies.find({})
            if i['cookie']
            and (i.get('FailedDate') != today)
            and (i.get("AuthFailed") < 10)]


def refresh_cookie(dct):
    """
    update cookie which is no longer available
    """
    new_cookie = getCookie(dct.get('account'))
    mongo_cli.cookies.find_one_and_update({'_id': dct['_id']},
                                          {'$set': {'cookie': new_cookie}})

def try_to_get_enough_cookies(CUSTOM_REFRESH=0):
    cookies = []
    for i in xrange(3):
        cookies = fetchCookies(CUSTOM_REFRESH)
        if len(cookies) >= 3:
            return cookies
        if i < 2:
            print "Not enough. Trying again..."
    return cookies

if __name__ == '__main__':

    try_to_get_enough_cookies(1)
    # myAccount = [
    #
    # ]
    # for line in ''''''.split():
    #     no, psw = line.split('----')
    #     myAccount.append({'no': no, 'psw': psw})
    # print myAccount.__repr__()
    # initCookies(myAccount)
    pass