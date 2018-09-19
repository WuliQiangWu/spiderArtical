# _*_ coding:utf-8 _*_
# __author__ : 'aj'
# __date__ : '2018/7/25 下午3:31'

import sys
import os
from scrapy.cmdline import execute

DIR_DICT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR_DICT)
# execute(['scrapy', 'crawl', 'jobbole'])
execute(['scrapy', 'crawl', 'lagou'])
