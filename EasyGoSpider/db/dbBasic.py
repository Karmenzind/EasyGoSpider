# coding: utf-8

import pymongo
import os
import mysql.connector
import yaml

class MongoBasic(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["EasyGoData"]
        self.cookies = db["cookies"]
        self.hmdata = db["heatmapdata"]
        self.cmd = db.command

if __name__ == '__main__':
    m = MongoBasic()
    # res = m.cookies.find_one({"_id": 0})
    # m.hmdata.insert({"_id":"2017060423"})
    import re
    for item in m.hmdata.find({}):
        tmp = re.match('\d+_(\d+)', item.pop('_id'))
        if tmp:
            m.hmdata.find_one_and_update({"_id":"2017060423"},
                                         {"$set":{tmp.group(1): item}})