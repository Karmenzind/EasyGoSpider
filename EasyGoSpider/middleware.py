# coding: utf-8
import random
import logging
from user_agents import agents
from EasyGoSpider.cookies import try_to_get_enough_cookies
from scrapy.exceptions import CloseSpider

logger = logging.getLogger(__name__)


class UserAgentMiddleware(object):
    """ change User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    """ change Cookie """
    logger.info("...start fetching cookies.")
    cookies = try_to_get_enough_cookies()
    if not cookies:
        raise CloseSpider("No available cookies")
    logger.info("Fetching Cookies Finished. Available num: %s" % len(cookies))

    def process_request(self, request, spider):
        if not self.cookies:
            raise CloseSpider("No available cookies")
        cookie = random.choice(self.cookies)
        request.cookies = cookie

