# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from datetime import datetime

from scrapy.http import Request
from scrapy.loader import ItemLoader

from spiderArtical.items import ArticleItem, ArticleItemLoader
from spiderArtical.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        获取文章列表中的文章url并交给scrapy下载后进行解析
        获取下一个页面的url并交给scrapy进行下载，并交给parse函数进行解析
        :param response:
        :return:
        """

        # 解析列表中的所有文章url
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')

        for post_node in post_nodes:
            # 利用Request的meta参数 可以传递一个字典过去，可以在self.meta里面取到指
            # 这个地方 scrapy提供了 嵌套的selector 方便选择
            front_image_url = post_node.css('img::attr(src)').extract_first('')
            post_url = post_node.css('::attr(href)').extract_first('')
            # 把循环出来的url交给scrapy下载并进行解析
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail,
                          meta={"front_image_url": parse.urljoin(response.url, front_image_url)})

        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        """
        解析文章的具体逻辑
        提取文章的具体字段
        :param response:
        :return:
        """

        # article_item = ArticleItem()

        # 通过css选择器提取字段

        # title = response.css('.entry-header h1::text').extract_first("")
        # create_date = response.css('p.entry-meta-hide-on-mobile::text').extract_first("").strip().replace('·',
        #                                                                                                   '').strip()
        # parsise_nums = response.css('.vote-post-up h10::text').extract_first("")
        # match_re = re.match('.*?(\d+).*', parsise_nums)
        # if match_re:
        #     parsise_nums = int(match_re.group(1))
        # else:
        #     parsise_nums = 0
        # fav_nums = response.css('.bookmark-btn::text').extract_first("")
        # match_re = re.match('.*?(\d+).*', fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('a[href="#artical-comment"] span::text').extract_first("")
        # match_re = re.match('.*?(\d+).*', comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.css('div.entry').extract_first("")
        # tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [ele for ele in tag_list if not ele.strip().endswith('评论')]
        # tags = ','.join(tag_list)
        #
        # article_item['title'] = title
        # try:
        #     create_date = datetime.strptime(create_date, '%Y/%m/%d').date()
        # except Exception as e:
        #     create_date = datetime.now().date()
        # article_item['create_date'] = create_date
        # article_item['url'] = response.url
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['front_image_url'] = [front_image_url]
        # article_item['parsise_nums'] = parsise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['tags'] = tags
        # article_item['content'] = content

        # 通过item_loader加载item
        item_loader = ArticleItemLoader(item=ArticleItem(), response=response)
        front_image_url = response.meta.get('front_image_url', '')  # 获取文章封面图
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('create_date', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_css('parsise_nums', '.vote-post-up h10::text')
        item_loader.add_css('fav_nums', '.bookmark-btn::text')
        item_loader.add_css('comment_nums', 'a[href="#artical-comment"] span::text')
        item_loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('content', 'div.entry')

        article_item = item_loader.load_item()

        yield article_item
