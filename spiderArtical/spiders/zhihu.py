# -*- coding: utf-8 -*-
import datetime
import json
import re
import time

import os
import scrapy
import pickle

from scrapy.loader import ItemLoader
from selenium import webdriver

from spiderArtical.items import ZhihuQuestionItem, ZhihuAnswerItem

try:
    from urllib import parse
except:
    import urlparse as parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers = {
        'host': 'www.zhihu.com',
        'referer': 'https://www.zhihu.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    start_answer_url = 'https://www.zhihu.com/api/v4/question/{0}/answer'

    def parse(self, response):
        """
        提取出html页面中的URL，并跟踪这些URL进行解析
        如果提取的URL中格式位/question/xxx就下载后进入解析函数
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url=url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$)", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交给提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(url=request_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        """
        处理question  页面，从页面中提取出具体的question item
        """
        if 'QuestionHeader-title' in response.text:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$)", response.url)
            if match_obj:
                question_id = int(match_obj.group(1))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css('title', 'h1.QuestionHeader-title::text')
            item_loader.add_css('content', '.QuestionHeader-detail')
            item_loader.add_value('url', response.url)
            item_loader.add_value('question_id', question_id)
            item_loader.add_css('answer_num', '.List-headerText span::text')
            item_loader.add_css('comment', '.QuestionHeader-actions button::text')
            item_loader.add_css('watcher_user_num', '.NumberBoard-value::text')
            item_loader.add_css('topics', '.QuestionHeader-topics .Popover::text')
            question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id), callback=self.parse_answer,
                             headers=self.headers)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        totals_answer = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']
        if not is_end:
            yield scrapy.Request(next_url, callback=self.parse_answer, headers=self.headers)
        # 提取answer具体字段
        for ans in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = ans['id']
            answer_item['url'] = ans['url']
            answer_item['question_id'] = ans['question']['id']

            answer_item['author_id'] = ans['author']['id'] if 'id' in ans['author'] else None
            answer_item['content'] = ans['content'] if 'content' in ans['content'] else None
            answer_item['praise_num'] = ans['voteup_count']
            answer_item['comments_num'] = ans['comments_count']
            answer_item['create_time'] = ans['created_time']
            answer_item['update_time'] = ans['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()
        yield answer_item

    def start_requests(self):
        browser = webdriver.Chrome(executable_path='/Users/aj/work/spiderArtical/chromedriver')
        browser.get(url='https://www.zhihu.com/')
        browser.find_element_by_css_selector('.SignContainer-switch span').click()
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('15838386917')
        browser.find_element_by_css_selector('.SignFlow-password .Input-wrapper input').send_keys('woshidage')
        browser.find_element_by_css_selector('.SignFlow-submitButton.Button--blue').click()
        time.sleep(5)
        cookies = browser.get_cookies()
        cookie_dict = {}

        current_path = os.path.dirname(os.path.dirname(__file__))
        for cookie in cookies:
            with open(current_path + '/cookies/' + cookie['name'] + '.zhihu', 'wb+') as f:
                pickle.dump(cookie, f)
                f.close()
                cookie_dict[cookie['name']] = cookie['value']
        # browser.close()

        # return [scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True, cookies=cookie_dict)]
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True, cookies=cookie_dict,
                             headers=self.headers)

        # def get_captcha(self):
        #     t = str(int(time.time() * 1000))
        #     captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)
        #
        # def start_requests(self):
        #     # return [scrapy.Request('https://www.zhihu.com/', headers=self.headers, callback=self.login)]
        #     browser = webdriver.Chrome(executable_path='/Users/aj/work/chromedriver')
        #     browser.get(url='https://www.zhihu.com/')
        #     browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper').send_keys('15838386917')
        #     browser.find_element_by_css_selector('.SignFlow-password .Input').send_keys('woshidage')
        #     browser.find_element_by_css_selector('.SignFlow-submitButton.Button--blue').click()
        #
        # def login(self, response):
        #     response_text = response.text
        #     march_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        #     xsrf = ''
        #     if march_obj:
        #         xsrf = march_obj.group(1)
        #
        #     if xsrf:
        #         post_url = "https://www.zhihu.com/login/phone_num"
        #         post_data = {
        #             "_xsrf": xsrf,
        #             "phone_num": "",
        #             "password": "",
        #         }
        #         return [scrapy.FormRequest(
        #             url=post_url,
        #             formdata=post_data,
        #             callback=self.check_login
        #         )]
        #
        # def check_login(self, response):
        #     # 验证服务器的返回数据判断是否成功
        #     text_json = json.loads(response.text)
        #     if "msg" in text_json and text_json["msg"] == "登录成功":
        #         for url in self.start_urls:
        #             yield scrapy.Request(url, dont_filter=True, headers=self.headers, callback=self.parse)
