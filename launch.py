# coding: utf-8

import time
import math
import os
import sched
import argparse
import sys
from scrapy import cmdline

parser = argparse.ArgumentParser(description="EasyGoSpider")
group = parser.add_mutually_exclusive_group()
group.add_argument("--now", action="store_true",
                   help="Launch right now and only once.")
group.add_argument("--loop", action="store_true",
                   help="Launch once every two hours from next even o'clock on.")
args = parser.parse_args()
schedule = sched.scheduler(time.time, time.sleep)


def next_time(t):
    next_t = list(t)
    if math.fmod(next_t[3], 2) == 0:
        next_t[3] += 2
    else:
        next_t[3] += 1
    next_t = next_t[:4] + [0 for i in range(5)]
    return next_t


def perform_command(cmd, inc):
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)


def timming_exe(cmd, inc):
    schedule.enter(inc, 0, perform_command, (cmd, 7200))
    schedule.run()


def loop():
    now = time.localtime()
    print "current time:", list(now)
    next_t = next_time(now)
    print "...will be started after", next_t
    interval = time.mktime(next_t) - time.mktime(now) + 10
    print "...wait for %s seconds" % interval
    timming_exe('scrapy crawl proc', interval)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        parser.print_help()
    elif args.now:
        cmdline.execute('scrapy crawl proc'.split())
    elif args.loop:
        loop()
