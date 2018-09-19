# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import MySQLdb
import MySQLdb.cursors

from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class SpiderarticalPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']
                item['front_image_url'] = image_file_path
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 利用scrapy提供的json export 导出json
    def __init__(self):
        self.file = open('jsonExport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'admin', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql_insert = '''
        insert into jobbole_article(title,url,create_date,fav_nums) VALUES (%s,%s,%s,%s)
        '''
        self.cursor.execute(sql_insert, (item['title'], item['url'], item['create_date'], item['fav_nums']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        mysql_param = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor
        )

        dbpool = adbapi.ConnectionPool('MySQLdb', **mysql_param)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_err, item, spider)

    def handle_err(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体插入逻辑
        sql_insert, params = item.get_insert_sql()
        cursor.execute(sql_insert, params)
