# coding: utf-8
import time
import datetime
import math
from scrapy import cmdline
import os
import sched

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
    # 安排inc秒后再次运行自己，即周期运行
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)


def timming_exe(cmd, inc):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(inc, 0, perform_command, (cmd, 7200))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()

if __name__ == "__main__":
    now = time.localtime()
    print "current time:", list(now)
    next_t = next_time(now)
    print "...will be started after", next_t
    interval = time.mktime(next_t) - time.mktime(now) + 10
    print "...wait for %s seconds" % interval
    # interval = 0
    import sys
    if len(sys.argv) > 1:
        interval = int(sys.argv[1])
    timming_exe('python launch.py', interval)



