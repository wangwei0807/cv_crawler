import copy
import json
import os

import scrapy
import traceback
from cv_crawler.common.account import zhilian
from cv_crawler.common.conf import zl_data
from cv_crawler.login.zhilian_login import ZLLogin


class ZhilianSpider(scrapy.Spider):
    name = 'zhilian'
    allowed_domains = ["zhilian.com"]
    cookies = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Referer': 'https://ihr.zhaopin.com/resumesearch/searchlist/?keyword=java',
        'X-Requested-With': "XMLHttpRequest",
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)

    def start_requests(self):
        # zl = ZLLogin(account=zhilian[0])
        # cansearch = 0
        # while cansearch == 0:
        #     zl.do_login()
        #     cansearch = zl.cansearch
        # self.cookies = zl.cookies
        with open('/'.join((os.getcwd(), 'cookie')), 'r') as f:
            self.cookies = json.loads(f.read())
        data = copy.deepcopy(zl_data)
        yield scrapy.Request(url='https://ihr.zhaopin.com/resumesearch/search.do?access_token=%s'
                                 % self.cookies.get('Token', ''), meta={'data': data}, callback=self.get_page,
                             dont_filter=True, headers=self.headers, cookies=self.cookies, method='POST',
                             body=json.dumps(data))

    def get_page(self, response):
        try:
            js = json.loads(response.text)
            h = copy.deepcopy(self.headers)
            h['Referer'] = response.url
            for i in js.get('results', []):
                yield scrapy.Request(url='http://ihr.zhaopin.com/resume/details/?resumeNo=%s_1&resumeSource=1&key=&%s'
                                     % (i['id'], i['valResumeTimeStr']), dont_filter=True, headers=h,
                                     cookies=self.cookies, callback=get_item)
        except:
            print(traceback.format_exc())

    def get_item(self, response):
        print(response.text)