# coding: utf-8
import random
import logging
from scrapy.crawler import Crawler
from user_agents import agents
from EasyGoSpider.cookies import try_to_get_enough_cookies
from EasyGoSpider import settings

logger = logging.getLogger(__name__)

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    """ change Cookie """
    logger.info("...start fetching cookies.")
    cookies = try_to_get_enough_cookies()
    if not cookies:
        raise AssertionError("No available cookies")
    logger.info("Fetching Cookies Finished. Available num: %s" % len(cookies))

    def process_request(self, request, spider):
        cookie = random.choice(self.cookies)
        request.cookies = cookie
        # logger.debug("current cookie is %r" % cookie)
