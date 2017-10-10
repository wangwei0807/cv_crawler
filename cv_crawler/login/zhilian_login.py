#!/usr/bin/env python
# encoding: utf8
import copy
import json
import logging
import os
import random
import re
import time
import traceback
import datetime

import math
import requests
from lxml import html
from selenium.common.exceptions import TimeoutException

from cv_crawler.captcha.hackedfuns import jsc_decode
from cv_crawler.captcha.lianzhong_api import get_coordinate
from cv_crawler.captcha.zhilianCaptcha import ZhilianCaptcha
from cv_crawler.common.account import zhilian
from cv_crawler.common.conf import PROJECT_PATH
from cv_crawler.common.logManager import get_logger
from cv_crawler.login.seleniumLogin import SeleniumLoginHacker


class ZLLogin(object):
    def __init__(self, account=None, server_port=40000):
        self.account = account
        self.port = server_port
        self.log_path = os.path.join(PROJECT_PATH, 'logs', 'ZLLogin')
        self.log_name = os.path.join(self.log_path,  datetime.datetime.now().strftime('%Y-%m-%d') + '.log')
        self.logger = get_logger(self.log_name, 10, logging.DEBUG)
        self.session = requests.session()
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'
        self.hacker = SeleniumLoginHacker(user_agent=self.user_agent, server_port=server_port)
        self.cookies = {}
        self.test_kw = ['销售', '产品经理', '财务', '金融', '交互设计', '开发']
        self.token = None
        self.cansearch = 0
        self.search_url = 'https://ihr.zhaopin.com/ihrapi/resume/resumesearch'

    def get_token(self):
        try:
            return self.get_cookie('Token', domain='.zhaopin.com')
        except:
            logging.error('Token is None')

    def get_cookie(self, cookiename, defaultv='', domain='', path='/'):
        curlckjar = self.session.cookies.get(cookiename, defaultv, domain, path)
        if curlckjar is None:
            return defaultv
        else:
            return curlckjar.value

    def _test_search(self):
        self.token = self.get_token()
        if "ihr.zhaopin.com" in self.search_url:
            self._test_can_search()
        else:
            logging.info(' is  old  version ! ! ! ')

    def _test_can_search(self):
        data = {
            'anyKeyWord': False,
            'onlyHasImg': False,
            'sortColumnName': 'sortUpDate',
            'sortColumn': 'sortUpDate desc',
            'startNum': '0',
            'rowsCount': '30',
            'keywords': self.test_kw[random.randint(0, 5)],
            'resumeGrade': ''
        }
        header = {'Referer': 'http://ihr.zhaopin.com/resumesearch/search/?keyword=%s' % data['keywords'],
                  'X-Requested-With': "XMLHttpRequest"}
        testsearch_url = 'https://ihr.zhaopin.com/resumesearch/search.do?access_token=%s' % self.token
        con1 = self.session.post(testsearch_url, data=json.dumps(data), headers=header)
        try:
            js = json.loads(con1.text.encode('utf-8'))
            num = js.get('numFound', '')
            if num:
                self.cansearch = 1
                self.login_state = '正常登录，能搜索'
                self.logger.info('登陆成功: %s, %s', self.account['u'], self.account['p'])
            else:
                self.login_state = '正常登录，不能查看简历'
                self.logger.warning('不能查看简历: %s, %s', self.account['u'], self.account['p'])
        except:
            self.cansearch = 0
            self.login_state = '不能搜索'
            self.logger.info('不能搜索: %s, %s', self.account['u'], self.account['p'])


    def resolve_captcha(self, con):
        cap = ZhilianCaptcha(con)
        return cap.resolve()

    def do_login(self):
        # self.hacker.update_chained_proxy('169.45.120.54:3128', 'shein', 'helloshein', True)# 代理地址，验证用户名，验证密码, 是否支持https
        cookies, page_source = self.hacker.hack2(self.account, captcha_resolver=self.resolve_captcha)
        self.apply_cookie(cookies)
        path = '/'.join((os.getcwd(), 'cookie'))
        self.cookie_to_disk(path)
        if page_source is None:
            print('----con is None')
            self.login_state = '网络请求失败'
            return False
        if u'>正在跳转<' in page_source:
            m = re.search('window\.location\.href = "(.*?)"', page_source, re.S)
            if m:
                url = m.group(1)
            else:
                m = re.search('''window.location.*,_\$\w{2}\((.*?)\)\);\}\);''', page_source)
                if not m:
                    self.login_state = '登陆后没能找到跳转链接'
                    return
                url = m.group(1).strip('\'"')
                self.logger.info("decrypted redirected url: %s", url)
                # if '/' in url:
                #     url = jsc_split_str(url)
                # else:
                #     url = jsc_decode(url)
            self.apply_cookie(cookies)
            path = '/' .join((os.getcwd(), 'cookie'))
            self.cookie_to_disk(path)
            # self.handle_login_redirect(url)
            # self.save_cookie_file('cookies.txt')
            # self._test_search()
            return True
        elif u'请选择你要登入的系统' in page_source:
            self.apply_cookie(cookies)
            con = self.session.get('http://rd2.zhaopin.com/s/loginmgr/loginproc_new.asp')
            self._test_search()
            return True
        elif u'您的密码存在被盗的风险' in page_source or u'您的密码存在被盗取的风险' in page_source:
            self.logger.info("password need change: %s, %s", self.account['u'], self.account['p'])
        #     self.logger.info("password need change: %s, %s", self.account['u'], self.account['p'])
        #     return self.on_account_security_risk(page_source)
        elif u'<p class="msg_tit_txt">为了确保您的账号安全，请使用手机验证码登录</p>' in page_source:
            self.login_state = "为了确保您的账号安全，请使用手机验证码登录"
            self.isvalid = False
            return False
        else:
            cdoc = html.fromstring(page_source)
            t = cdoc.xpath("//form[@id='form1']//div[@class='msg_error']")
            logging.error('登录失败！')
            if t is not None and len(t) > 0:
                xt = t[0].text_content().strip()
                if u'验证码错误' in xt:
                    self.login_state = "登录失败，验证码错误"
                    self.logger.warning('验证码错误')
                elif u'用户名或密码错误' in xt:
                    self.isvalid = False
                    self.login_state = "用户名密码错误"
                elif u'存在异常行为，已被暂时冻结' in xt:
                    self.isvalid = False
                    self.login_state = "存在异常行为，已被暂时冻结"
                elif u'您的账户已被冻结' in xt:
                    self.isvalid = False
                    self.login_state = "您的账户已被冻结"
                elif u'频繁' in xt:
                    self.isvalid = False
                    self.login_state = "频繁操作，被限制"
                    # raise LoginErrors.AccountHoldError
                elif u'密码必须在6~12位之间' in xt:
                    self.isvalid = False
                    self.login_state = "密码太长或太短"
                    # raise LoginErrors.AccountHoldError
                    # elif u'请勾选协议后登录' in xt:
                    # raise LoginErrors.AccountHoldError
                elif u'您的账号状态异常' in xt:
                    self.login_state = "你的账号状态异常"
                    self.isvalid = False
                    # raise LoginErrors.AccountHoldError
                self.logger.info('%s: %s, %s', xt, self.account['u'], self.account['p'])
                self.login_state = xt.decode('utf-8') if isinstance(xt, bytes) else xt
            return False

    def apply_cookie(self, cookies):
        for ck in cookies:
            self.cookies[ck['name']] = ck['value']
            self.session.cookies.set(ck['name'], ck['value'], domain=ck['domain'], path=ck['path'])
            # if "FSSBBIl1UgzbN7N" in ck['name']:
            #     self.cookies.append('rdsearch.zhaopin.com', ck['name'], ck['value'], expires=ck['expiry'],
            #                     secure=ck['secure'],
            #                     path=ck['path'])
            #     self.add_cookie('rd2.zhaopin.com', ck['name'], ck['value'], expires=ck['expiry'],
            #                     secure=ck['secure'],
            #                     path=ck['path'])
            # self.add_cookie(ck['domain'], ck['name'], ck['value'], expires=ck['expiry'], secure=ck['secure'],
            #                 path=ck['path'])

    def find_value(self, cookies, domain, key):
        v = cookies.get(domain, {}).get('/', {}).get(key, None)
        if v:
            return v.value
        return None

    def handle_login_redirect(self, url):
        con = self.session.get(url)
        self.logger.debug(con.headers)
        if u'选择登录机构' in con.text:
            m = re.findall('onClick="submitpoint\((\d+)\)', con.text, re.S)
            if m and len(m) > 0:
                url = 'https://rd2.zhaopin.com/s/loginmgr/loginpoint.asp?id=%s&BkUrl=&deplogincount=%d' % (
                    m[0], len(m) - 1)
                self.session.get(url, headers={'Referer': 'http://rd2.zhaopin.com/s/loginmgr/choose.asp'})
            self._old_version = True
        else:
            self._old_version = "Location: https://ihr.zhaopin.com" not in con.headers

    def cookie_to_disk(self, name='cookie'):
        with open(name, 'w+') as f:
            f.write(json.dumps(self.cookies))
            f.flush()

__encrypted_short_str__ = "qrcklmDoExthWJiHAp1sVYKU3RFMQw8IGfPO92bvLNj.7zXBaSnu0TC6gy_4Ze5d"

__qrck__ = []

def jsc_qrck():
    if len(__qrck__) > 0:
        return __qrck__
    for c in __encrypted_short_str__:
        __qrck__.append(c)
    return __qrck__


def splits(arr, min_i, max_i, step):
    mid = int(math.floor((min_i + max_i) / 2.0))
    if step > 0:
        step -= 1
        if mid - min_i >= 3:
            splits(arr, min_i, mid, step)
        if max_i - mid >= 3:
            splits(arr, mid, max_i, step)
    for i in range(min_i, mid, 2):
        v = arr[i]
        w = max_i - 1 - i + min_i
        arr[i] = arr[w]
        arr[w] = v

def jsc_split_str(s):
    v = list(s)
    splits(v, 0, len(v), 2)
    return ''.join(v)





if __name__ == '__main__':
    zl = ZLLogin(account=zhilian[0])
    zl.do_login()
