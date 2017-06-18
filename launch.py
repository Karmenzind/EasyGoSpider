# coding: utf-8
import sys
from scrapy import cmdline
import time
from EasyGoSpider.db.dbBasic import MongoBasic
from EasyGoSpider.cookies import try_to_get_enough_cookies


if len(sys.argv) > 1:
    try_to_get_enough_cookies(0)
else:
    try_to_get_enough_cookies(1)
mongo_cli = MongoBasic()
START_HOUR = time.strftime("%Y%m%d%H", time.localtime())

while 1:
    find_res = mongo_cli.hmdata.find_one({"_id": START_HOUR})
    find_num = len(find_res) if find_res else 0
    completeness = find_num == 67
    if completeness:
        print "Completed already. :)"
        break

    current_hour = time.strftime("%Y%m%d%H", time.localtime())
    if (current_hour != START_HOUR) or (completeness == 1):
        print "It's already %s. Stopping..." % current_hour
        break

    cmdline.execute("scrapy crawl EasyGoSpider".split())
