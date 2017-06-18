# coding: utf-8
import random
from user_agents import agents
from EasyGoSpider.cookies import try_to_get_enough_cookies

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    """ 换Cookie """
    print "...start fetching cookies."
    cookies = try_to_get_enough_cookies()
    if not cookies:
        raise AssertionError("No available cookies")
    print "Fetching Cookies Finished. Available num:", len(cookies)

    def process_request(self, request, spider):
        cookie = random.choice(self.cookies)
        request.cookies = cookie
