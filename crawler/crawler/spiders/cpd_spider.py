#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : 张旭
# @Email   : zhangxu3486432@gmail.com
# @Blog    : https://zhangxu3486432.github.io
# @FileName: cpd_spider.py
# @Time    : 2020/1/16


import logging
import os
import re
from datetime import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings
from scrapy.utils.request import request_fingerprint

from crawler.items import CpdItem

settings = get_project_settings()

logger = logging.getLogger(__name__)


class CpdSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(CpdSpider, self).__init__(*args, **kwargs)

    name = "cpd"

    custom_settings = {
        'LOG_FILE': f"log/{name}/crawler_{datetime.now().strftime('%Y.%m.%d_%H:%M:%S')}.log"
    }

    database_name = 'news'
    table_name = 'cpd_news_content'
    filter_name = 'request_id'

    allowed_domains = ["cpd.com.cn"]

    start_urls = [
        # 'http://www.cpd.com.cn/',
        'http://www.cpd.com.cn/n10216060/n10216158/',

        # 'http://news.cpd.com.cn/',
        'http://news.cpd.com.cn/n18151/',
        'http://news.cpd.com.cn/n3559/',
        'http://news.cpd.com.cn/n3569/',
        'http://news.cpd.com.cn/n3573/',

        # 'http://jt.cpd.com.cn/',
        'http://jt.cpd.com.cn/n462015/',
        'http://jt.cpd.com.cn/n462009/',
        'http://jt.cpd.com.cn/n462051/',
        'http://jt.cpd.com.cn/n462013/',
        'http://jt.cpd.com.cn/n464703/',
        'http://jt.cpd.com.cn/n462037/',
        'http://jt.cpd.com.cn/n462031/',
        'http://jt.cpd.com.cn/n462049/',
        'http://jt.cpd.com.cn/n462059/',
        'http://jt.cpd.com.cn/n462061/',
        'http://jt.cpd.com.cn/n462053/',
        'http://jt.cpd.com.cn/n462027/',

        # 'http://zhian.cpd.com.cn/',
        'http://zhian.cpd.com.cn/n26237006/',
        'http://zhian.cpd.com.cn/n26237008/',
        'http://zhian.cpd.com.cn/n26237014/',

        # 'http://minsheng.cpd.com.cn/',
        'http://minsheng.cpd.com.cn/n1448484/',
        'http://minsheng.cpd.com.cn/n1448482/',
        'http://minsheng.cpd.com.cn/n1448490/',
        'http://minsheng.cpd.com.cn/n1448494/',
        'http://minsheng.cpd.com.cn/n1448492/'
    ]

    link = LinkExtractor(allow=start_urls, deny='.*?<script>document\.write\(location\.href\);</script>')

    # # http://zhian.cpd.com.cn/n26237006/
    # p_index = re.compile('createPageHTML\((\d+), (\d+),')
    # next_index = self.p_index.findall(next_index_html)  # [(总页数， 当前页数)]

    # http://zhian.cpd.com.cn/n26237006/
    # http://jt.cpd.com.cn/n462015/
    # [(当前页数， 总页数)]
    p_index = re.compile('var currentPage = (\d+);.*?var countPage = (\d+)//', re.S)

    # http://jt.cpd.com.cn/n462015/c4191056/content.html
    p_news1 = re.compile('createPageHTML\((\d+), (\d+),')

    # 'http://minsheng.cpd.com.cn/n1448492/c3834444/content.html'
    p_news2 = re.compile('var maxPageNum=(\d+);.*?var pageName = (\d+);', re.S)

    # http://zhian.cpd.com.cn/n26237006/202001/t20200120_877942.html
    p_path1 = re.compile('(.*/)(.*?_.*?)\.html')

    # 'http://jt.cpd.com.cn/n462015/c4191056/content.html'
    p_path2 = re.compile('(.*?)content.html')

    def start_requests(self):
        try:
            path = f'error/{self.name}'
            retry_file = os.path.join(path, 'retry.tsv')
            with open(retry_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    news_url = line.split('\t')[0]
                    yield scrapy.Request(url=news_url, callback=self.parse_news)
        except IOError:
            logger.info('retry.tsv not accessible')

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_index, dont_filter=True)

    def parse_index(self, response):
        url = response.url
        next_index_html = response.xpath('//*[@id="newslist"]/div//script').get()
        next_index = self.p_index.findall(next_index_html)  # [(当前页数， 总页数)]

        if len(next_index) == 1 and next_index[0][1] != '0' and next_index[0][0] == '0':
            for page in range(1, int(next_index[0][1])):
                yield scrapy.Request(url=f'{url}index_{page}.html', callback=self.parse_news)

    def parse_news(self, response):
        url = response.url
        title = response.xpath('//*[@id="newslist"]/h1/gettitle/text()').get()

        # 判断是 index 页面，还是 news 页面
        if title is not None:
            next_page_html = response.xpath('//*[@id="autopage"]//script').get()

            current_page = response.meta.get('page', 1)
            total_page = 1

            next_page1 = self.p_news1.findall(next_page_html)  # [(总页数 0，当前页数 0)] 从 0 计数
            next_page2 = self.p_news2.findall(next_page_html)  # [(总页数 1，当前页数 1)] 从 1 计数
            if len(next_page1) == 1 and next_page1[0][0] != '0' and next_page1[0][1] == '0':
                total_page = int(next_page1[0][0])
                url_arr = self.p_path1.findall(url)
                if len(url_arr) == 1:
                    for page in range(1, int(next_page1[0][0])):
                        yield scrapy.Request(url=f'{url_arr[0][0]}{url_arr[0][1]}_{page}.html',
                                             callback=self.parse_news, meta={'page': page + 1})
                else:
                    self.logger.error(f'未知格式的 NEWS URL: {url}')
            elif len(next_page2) == 1 and next_page2[0][0] != '1' and next_page2[0][1] == '1':
                total_page = int(next_page2[0][0])
                url_arr = self.p_path2.findall(url)
                if len(url_arr) == 1:
                    for page in range(2, int(next_page2[0][0]) + 1):
                        yield scrapy.Request(url=f'{url_arr[0]}content_{page}.html', callback=self.parse_news,
                                             meta={'page': page})
                else:
                    self.logger.error(f'未知格式的 NEWS URL: {url}')

            fp = request_fingerprint(response.request)

            cpd_item = ItemLoader(item=CpdItem(), response=response)
            cpd_item.add_value('request_id', fp)
            cpd_item.add_value('url', url)
            cpd_item.add_xpath('title', '//*[@id="newslist"]/h1/gettitle/text()')
            cpd_item.add_xpath('content', '//*[@id="fz_test"]/div[1]/table')
            cpd_item.add_value('category', url)
            cpd_item.add_xpath('source', '//*[@id="source_report"]/text()')
            cpd_item.add_xpath('date', '//*[@id="pub_time_report"]/text()')
            cpd_item.add_value('news_id', url)
            cpd_item.add_value('page', current_page)
            cpd_item.add_value('total_page', total_page)
            yield cpd_item.load_item()

        links = self.link.extract_links(response)
        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse_news)
