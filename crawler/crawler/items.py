# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import logging
import re

from scrapy import Item, Field
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags, remove_tags_with_content

logger = logging.getLogger(__name__)


class CrawlerItem(Item):
    pass


p1 = re.compile('.*/(.*?)/content_\d+\.html|.*/(.*?)/content\.html|.*/(.*?_.*?)_(\d.*?)\.html|.*/(.*?)\.html')
p2 = re.compile('http://.*?/(.*?)/.*')

category = {
    'n10216060': '关注',
    'n18151': '时政',
    'n3559': '公安要闻',
    'n3569': '政法',
    'n3573': '评论',
    'n462015': '公路',
    'n462009': '交管信息',
    'n462051': '交警风采',
    'n462013': '交通频道',
    'n464703': '时事观察',
    'n462037': '警用装备',
    'n462031': '专题活动',
    'n462049': '交企展播',
    'n462059': '安全宣传',
    'n462061': '文明交通',
    'n462053': '图说交通',
    'n462027': '能源环保',
    'n26237006': '工作动态',
    'n26237008': '案件聚焦',
    'n26237014': '综合治理',
    'n1448484': '社会瞭望',
    'n1448482': '民生聚焦',
    'n1448490': '民生警务',
    'n1448494': '反腐倡廉',
    'n1448492': '要案追踪',
}


def clean(value):
    value = value.replace('\t', ' ')
    return value.strip()


def remove_style(value):
    value = remove_tags_with_content(value, which_ones=('style',))
    value = remove_tags(value)
    value = value.replace('\t', ' ')
    value = value.strip()
    return value


def get_news_id(url):
    res = p1.match(url)
    if res:
        res = res.groups()
        # (None, None, 't20200120_877942', '2', None)
        if res[2]:
            return res[2]
        res = set(res)
        res.remove(None)
        return res.pop()
    logger.error('Cannot extract news_id from url.')
    return ''


def get_category(url):
    path = p2.search(url)
    if path:
        return category[path[1]]
    logger.error('Unknown category.')
    return '其他'


class CpdItem(Item):
    request_id = Field(
        output_processor=TakeFirst(),
    )
    url = Field(
        output_processor=TakeFirst(),
    )
    title = Field(
        input_processor=MapCompose(clean),
        output_processor=Join(),
    )
    content = Field(
        input_processor=MapCompose(remove_style, ),
        output_processor=Join(),
    )
    category = Field(
        input_processor=MapCompose(get_category, ),
        output_processor=Join(),
    )
    source = Field(
        input_processor=MapCompose(clean),
        output_processor=TakeFirst(),
    )
    date = Field(
        input_processor=MapCompose(clean),
        output_processor=TakeFirst(),
    )
    news_id = Field(
        input_processor=MapCompose(get_news_id),
        output_processor=TakeFirst(),
    )
    page = Field(
        output_processor=TakeFirst(),
    )
    total_page = Field(
        output_processor=TakeFirst(),
    )
