# coding: utf-8
import random
import json
import datetime
from user_agents import agents
from db.dbBasic import mongo_cli
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class UserAgentMiddleware(object):
    """ change User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    """ change Cookie """

    def process_request(self, request, spider):
        cookie = random.choice(spider.cookies)
        request.cookies = cookie


class LocalRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        # customiz' here
        resp_dct = json.loads(response.body)
        if resp_dct.get('code') != 0:
            if resp_dct.get('code') == -100:
                # or resp_dct.get("data") == "\\u8be5\\u7528\\u6237\\u8bbf\\u95ee\\u6b21\\u6570\\u8fc7\\u591a".decode(
                # 'unicode_escape'):  # 访问次数过多
                banned_cookie = request.cookies
                spider.cookies.remove(banned_cookie)
                spider.logger.info("Temporarily BANNED: %s." % banned_cookie)
                spider.logger.info("%s cookies left." % len(spider.cookies))
                mongo_cli.cookies.find_one_and_update({"cookie": banned_cookie},
                                                      {"$set": {"FailedDate": str(datetime.date.today())}})
            spider.logger.warning("Url %s %s is rescheduled ." % (spider.all_urls[request.url],
                                                                  request.url))
            return self._retry(request, response.body, spider) or response

        return response
