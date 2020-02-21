# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class SavePipeline(object):

    def __init__(self):
        host = settings.get('MYSQL_HOST', 'localhost')
        mysql_user = settings.get('MYSQL_USER', 'root')
        mysql_pwd = settings.get('MYSQL_PASSWORD', 'news_crawler')
        mysql_port = settings.get('MYSQL_PORT', 3306)
        self.db = pymysql.connect(host=host, user=mysql_user, password=mysql_pwd, port=mysql_port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        sql_news = """INSERT INTO
        news.cpd_news (news_id, title, category, source, publish_date, page_total)
        VALUES (%s,%s,%s,%s,%s,%s)
        """
        sql_content = """INSERT INTO
        news.cpd_news_content (news_id, request_id, url, content, page)
        VALUES (%s,%s,%s,%s,%s)
        """
        request_id = item.get('request_id', '')
        url = item.get('url', '')
        title = item.get('title', '')
        content = item.get('content', '')
        category = item.get('category', '')
        source = item.get('source', '')
        date = item.get('publish_date', '')
        news_id = item.get('news_id', '')
        page = item.get('page', 0)
        total_page = item.get('total_page', 0)

        try:
            self.cursor.execute(sql_content, (news_id, request_id, url, content, page))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            if e.args[0] == 1452:
                try:
                    self.cursor.execute(sql_news, (news_id, title, category, source, date, total_page))
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    spider.logger.error(e)
                try:
                    self.cursor.execute(sql_content, (news_id, request_id, url, content, page))
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    spider.logger.error(e)
            else:
                spider.logger.error(f'occur error when db commit date: {e.args[1]}; url: {item.get("url", "")}')
        return

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
