# coding: utf-8
# Scrapy settings for properties project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import yaml

BOT_NAME = 'EasyGoSpider'

SPIDER_MODULES = ['EasyGoSpider.spiders']
NEWSPIDER_MODULE = 'EasyGoSpider.spiders'

# Crawl responsibly by identifying yourself (and your website) on
# the user-agent
#USER_AGENT = 'EasyGoSpider (+http://www.yourdomain.com)'

with open('./EasyGoSpider/headers.yaml') as f:
    _headers = yaml.load(f)
DEFAULT_REQUEST_HEADERS = _headers

# Disable S3
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

#  orig * 100000
LAT_STEP = 50000 # Divided into N squares
LNG_STEP = 30000
LAT = [30519681, 30791396, LAT_STEP]
LNG = [103904185, 104205148, LNG_STEP]
# http://c.easygo.qq.com/api/egc/heatmapdata?lng_min=103.934185&lat_max=50030.769681&lng_max=30103.934185&lat_min=30.769681&level=16&city=%E6%88%90%E9%83%BD&lat=&lng=&_token=

DOWNLOADER_MIDDLEWARES = {
    "EasyGoSpider.middleware.UserAgentMiddleware": 401,
    "EasyGoSpider.middleware.CookiesMiddleware": 402,
}

ITEM_PIPELINES = {
    'EasyGoSpider.pipelines.MongoDBPipleline': 300,
}

DOWNLOAD_DELAY = 1
LOG_LEVEL = 'INFO'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

RETRY_ENABLED = 1
RETRY_TIMES = 10

REFRESH_TOKENS = 0 # 重新获取所有账号的Token
CAPTCHA_RECOGNIZ = 2 # 1: 人工输入 2: 云打码