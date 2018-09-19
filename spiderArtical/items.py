# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from datetime import datetime
from w3lib.html import remove_tags
from .settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT


class SpiderarticalItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 把字符串时间变成date类型的时间
def date_format(value):
    try:
        value = datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        value = datetime.now().date()
    return value


# 定义只取第一个值的item loader
class ArticleItemLoader(ItemLoader):
    default_loader_context = TakeFirst()


# 正则验证数字
def get_nums(value):
    match_re = re.match('.*?(\d+).*', value)
    if match_re:
        comment_nums = int(match_re.group(1))
    else:
        comment_nums = 0

    return comment_nums


# 去掉评论
def remove_comment_tags(value):
    if '评论' in value:
        return ''
    else:
        return value


# 返回原来的值
def return_value(value):
    return value


class ArticleItem(scrapy.Item):
    title = scrapy.Field(input_processor=MapCompose())
    create_date = scrapy.Field(
        input_processor=MapCompose(date_format)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    parsise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watcher_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()


class LagouItemLoader(ItemLoader):
    default_loader_context = TakeFirst()


def remove_splash(value):
    # 去掉斜线
    return value.replace('/', '')


def remove_html_tag(value):
    # 去掉html的tag
    return remove_tags(value)


def handel_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field()
    degree_need = scrapy.Field()
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handel_jobaddr)
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO lagou_job(title,url,url_object_id,salary,job_city,work_years,degree_need,job_type,publish_time,job_advantage,job_desc,job_addr,company_name,company_url,tags,crawl_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,,%s,%s,%s,%s,%s,,%s,%s,%s,%s,%s,) ON DUPLICATE KEY UPDATE salary=VALUES (salary),job_desc=VALUES (job_desc)
        """
        params = (
            self['title'],
            self['url'],
            self['url_object_id'],
            self['salary'],
            self['job_city'],
            self['work_years'],
            self['degree_need'],
            self['job_type'],
            self['publish_time'],
            self['job_advantage'],
            self['job_desc'],
            self['job_addr'],
            self['company_name'],
            self['company_url'],
            self['tags'],
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )
        return insert_sql, params
