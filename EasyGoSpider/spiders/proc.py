# coding: utf-8

from scrapy.loader import ItemLoader
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from EasyGoSpider.cookies import mongo_cli
from EasyGoSpider import settings
from EasyGoSpider.items import HeatMapItem
import json
import time

START_HOUR = time.strftime("%Y%m%d%H", time.localtime())

def start_url_gen():
    lats = range(*(settings.LAT)) # don't use xrange here
    lngs = range(*(settings.LNG))
    base = 'http://c.easygo.qq.com/api/egc/heatmapdata?' \
           'lng_min={lng_min}' \
           '&lat_max={lat_max}' \
           '&lng_max={lng_max}' \
           '&lat_min={lat_min}' \
           '&level=16' \
           '&city=%E6%88%90%E9%83%BD' \
           '&lat=undefined' \
           '&lng=undefined' \
           '&_token='
    for x, lat_m in enumerate(lats):
        for y, lng_m in enumerate(lngs):
            scale = 1000000.0

            # current_hour = '1234'
            find_res = mongo_cli.hmdata.find_one({"_id": START_HOUR})
            item_idx = x*len(lngs) + y # idx in mongo. Not usual idx
            if find_res and find_res.has_key(str(item_idx)): # already in mongo
                continue
            else:
                url = base.format(lat_min=lat_m / scale,
                                  lat_max=(lat_m + settings.LAT_STEP) / scale,
                                  lng_min=lng_m / scale,
                                  lng_max=(lng_m + settings.LNG_STEP) / scale)
                yield url, item_idx


class BasicSpider(CrawlSpider):
    name = "EasyGoSpider"
    # http://c.easygo.qq.com/api/egc/heatmapdata?lng_min=104.060931&lat_max=30.666652&lng_max=104.090931&lat_min=30.616651999999998&level=16&city=%E6%88%90%E9%83%BD&lat=30.651652&lng=104.075931&_token=
    allowed_domains = ["c.easygo.qq.com"]

    all_urls = dict(start_url_gen())
    finished = []

    def start_requests(self):
        claimed = ''
        loop = 0
        while len(self.finished) < len(self.all_urls):
            # EXIT condition 1
            # if loop > 5:
            #     print "...will be restarted. "
            #     return  # no sys.exit here
            # loop += 1
            # EXIT condition 2
            current_hour = time.strftime("%Y%m%d%H", time.localtime())
            if current_hour != START_HOUR:
                print "It's already %s. Stopping..." % current_hour
                return
            percentage = 66*len(self.finished)/len(self.all_urls)
            bar = '#'*percentage + '-'*(66-percentage)
            claim = u'Crawled %s / %s. Continuing... |%s|' % (len(self.finished), len(self.all_urls), bar)
            if claim != claimed:
                claimed = claim
                print claim
            for url, item_idx in self.all_urls.iteritems():
                if item_idx in self.finished:
                    continue
                else:
                    yield Request(url, callback=self.parse_item)
        print u'Crawled %s / %s. Done :)' % (len(self.finished), len(self.all_urls))

    def parse_item(self, response):
        """ This function parses a property page.
        """
        url = response.url
        item_idx = self.all_urls[url]
        print "Trying page ", item_idx, url

        resp_dct = json.loads(response.body)
        if resp_dct.get('code') == 0:
            # Create the loader using the response
            l = ItemLoader(item=HeatMapItem(), response=response)
            # Housekeeping fields
            current_hour = time.strftime("%Y%m%d%H", time.localtime())
            l.add_value('cur_hour', current_hour)
            l.add_value('serial', item_idx)
            l.add_value('data', resp_dct.pop('data'))
            l.add_value('timestamp', resp_dct.pop('nt'))
            l.add_value('others', resp_dct)
            l.add_value('url', url)
            l.add_value('is_parsed', 0)

            self.finished.append(item_idx)
            print u"Crawling %s, %s successfully. :)" % (item_idx, url)
            yield l.load_item()
        else:
            if resp_dct.get("data") == "\\u8be5\\u7528\\u6237\\u8bbf\\u95ee\\u6b21\\u6570\\u8fc7\\u591a".decode('unicode_escape'): # 访问次数过多
                banned_cookie = response.request.cookies
                yield {"BannedCookieToday": banned_cookie}
            else:
                yield {}
            print u"Crawling %s, %s failed. :(" % (item_idx, response.url)

if __name__ == '__main__':
    a = list(start_url_gen())
    print len(a)
