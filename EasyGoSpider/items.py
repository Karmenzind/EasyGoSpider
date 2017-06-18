# coding: utf-8

from scrapy.item import Item, Field


class HeatMapItem(Item):
    # Primary fields
    cur_hour = Field()
    serial = Field()

    # Housekeeping fields
    url = Field()
    is_parsed = Field()

    # build-in
    data = Field()
    timestamp = Field()
    others = Field() # code scale flag max_data



if __name__ == '__main__':
    h = HeatMapItem()
