# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from spiderArtical.items import LagouItemLoader, LagouJobItem

from spiderArtical.utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'zhaopin/.*'), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        item_oader = LagouItemLoader(item=LagouJobItem(), response=response)
        # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # i['name'] = response.xpath('//div[@id="name"]').extract()
        # i['description'] = response.xpath('//div[@id="description"]').extract()
        item_oader.add_css('title', '.job-name::attr(title)')
        item_oader.add_value('url', response.url)
        item_oader.add_value('url_object_id', get_md5(response.url))
        item_oader.add_css('salary', '.job_request .salary::text')
        item_oader.add_xpath('job_city', '//*[@class="job_request"]/p/span[2]/text()')
        item_oader.add_xpath('work_years', '//*[@class="job_request"]/p/span[2]/text()')
        item_oader.add_xpath('degree_need', '//*[@class="job_request"]/p/span[4]/text()')
        item_oader.add_xpath('job_type', '//*[@class="job_request"]/p/span[5]/text()')
        item_oader.add_css('tags', '.position-label li::text')
        item_oader.add_css('publish_time', '.publish_time::text')
        item_oader.add_css('job_advantage', '.job_advantage p::text')
        item_oader.add_css('job_desc', '.job_bt div::text')
        item_oader.add_css('job_addr', '.job_address .work_addr')
        item_oader.add_css('company_name', '#job_company dt a img::attr(alt)::text')
        item_oader.add_css('company_url', '#job_company dt a::attr(url)::text')
        item_oader.add_value('crawl_time', datetime.now())

        job_item = item_oader.load_item()
        return job_item
