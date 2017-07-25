# coding: utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import datetime
import logging
from EasyGoSpider.items import HeatMapItem

logger = logging.getLogger(__name__)


class MongoDBPipleline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["EasyGoData"]
        self.cookies = db["cookies"]
        self.hmdata = db["heatmapdata"]

    def process_item(self, item, spider):
        if isinstance(item, HeatMapItem):
            try:
                _id = item.pop('cur_hour')[0]
                serial = str(item.pop('serial')[0])
                if not self.hmdata.find_one({'_id': _id}):
                    self.hmdata.insert({'_id': _id})
                self.hmdata.find_one_and_update({'_id': _id},
                                                {"$set": {serial: item}})
            except Exception, e:
                logger.info(e.__class__.__name__, e)
        return item
