import base64
import os
import time

import re
from platform import system

import chardet
from browsermobproxy import Server,Client
from selenium.webdriver import FirefoxProfile, DesiredCapabilities, Firefox, ActionChains
from cv_crawler.common.logManager import get_logger
from cv_crawler.login.xvfb import Xvfb

logging = get_logger(os.getcwd()+'/logs/login.log', 10, True)

def is_osx():
    return system() == 'Windows'

def get_browsermob_proxy():
    bsp = os.environ.get('BROWSERMOB_PATH')
    if bsp is None:
        bsp = os.path.dirname(__file__) + '/browsermob/'
    logging.debug("browsermob path: %s", bsp)
    if os.path.exists(bsp):
        brwpfile = bsp + '/bin/browsermob-proxy'
        if os.path.exists(brwpfile):
            return brwpfile
        raise RuntimeError("failed to find browsermob-proxy in BROWSERMOB_PATH %s" % bsp)
    raise RuntimeError("failed to find browsermob-proxy path")

def start_firefox(proxy=None, user_agent=None):
    p = FirefoxProfile("E://profiles")
    p.accept_untrusted_certs = True
    if user_agent:
        p.set_preference("general.useragent.override", user_agent)
    capabilities = DesiredCapabilities().FIREFOX.copy()
    capabilities['acceptInsecureCerts'] = True

    if proxy:
        p.set_proxy(proxy)
    browser = Firefox(firefox_profile=p, capabilities=capabilities)
    return browser

class SeleniumLoginHacker(object):
    def __init__(self, server_port=40000, chained_proxy=None, proxy_username=None, proxy_passowrd=None, is_https=False,
                 user_agent=None):
        self.account = {'u': 'username', 'p': 'password'}
        self.proxy_server = None
        self.proxy = None
        self.browser = None
        self.short_sleep = 0.5
        self.mid_sleep = 1
        self.server_port = server_port
        self.chained_proxy = chained_proxy
        self.proxy_username = proxy_username
        self.proxy_password = proxy_passowrd
        self.long_sleep = 3
        self.is_https = is_https
        self.port = None
        self.user_agent = user_agent

    def update_chained_proxy(self, chained_proxy, username, password, is_https=False):
        self.chained_proxy = chained_proxy
        self.proxy_username = username
        self.proxy_password = password
        self.is_https = is_https

    def init_proxy_server(self, port=None):
        kwargs = {}
        if port is not None:
            kwargs['port'] = port
        if self.chained_proxy is not None:
            if self.is_https:
                kwargs['httpsProxy'] = self.chained_proxy
            else:
                kwargs['httpProxy'] = self.chained_proxy
        if self.proxy_username is not None:
            kwargs['proxyUsername'] = self.proxy_username
        if self.proxy_password is not None:
            kwargs['proxyPassword'] = self.proxy_password
        server = Server('C://browsermob-proxy//bin//browsermob-proxy.bat', options={"port": self.server_port})
        server.start()
        proxy = server.create_proxy(params=kwargs)
        return server, proxy

    def init_hacker(self):
        if self.proxy_server is None:
            self.proxy_server, self.proxy = self.init_proxy_server(self.port)
            if self.proxy is None:
                raise RuntimeError("failed to init proxy")
            self.port = self.proxy.port
            self.browser = start_firefox(self.proxy.selenium_proxy(), self.user_agent)
            logging.info("hacker initialized")
        else:
            logging.debug("hacker is initialized before")

    def request_index(self):
        cnt = 5
        while cnt > 0:
            self.browser.get('https://passport.zhaopin.com/org/login')
            time.sleep(self.long_sleep)
            # TODO:  check browser page
            m = re.search('id="CheckCodeCapt"', self.browser.page_source)
            cnt -= 1
            if m:
                return True
        return False

    def fill_in_form(self):
        self.browser.execute_script(
            "document.getElementById('LoginName').setAttribute('value', '%s');" % self.account['u'])
        self.browser.execute_script(
            "document.getElementById('Password').setAttribute('value', '%s');" % self.account['p'])

    def get_captcha(self):
        self.proxy.new_har(options={"captureBinaryContent": True, "captureContent": True})
        cap = self.browser.find_element_by_xpath('//input[@id="CheckCodeCapt"]')
        time.sleep(1)
        if not cap:
            logging.error("failed to find captcha button")
            return
        cap.click()
        self.proxy.wait_for_traffic_to_stop(6, 60)
        captcha = self.browser.find_element_by_id('captcha')
        if captcha is None:
            logging.warning("cannot find captcha element")
        elif 'block' not in captcha.value_of_css_property('display'):
            logging.warning("captcha element not show")
        time.sleep(10)
        entries = self.proxy.har['log']['entries']
        i = len(entries) - 1
        while i >= 0:
            en = entries[i]
            i -= 1
            if re.match('https://passport.zhaopin.com/chk/getcap\?t\d+', en['request']['url']):
                return base64.b64decode(en['response']['content']['text'])
        logging.warning("none captcha")
        return None

    def simulate_verify(self, codes):
        cap = self.browser.find_element_by_id('captcha-body')
        if cap is None:
            logging.error("captcha body not found")
            return
        actions = ActionChains(self.browser)
        actions.move_to_element(cap).perform()
        for x, y in codes:
            print(x, y)
            actions = ActionChains(self.browser)
            actions.move_to_element_with_offset(cap, x, y).click().perform()
            time.sleep(self.short_sleep)
        time.sleep(self.mid_sleep)
        btn = self.browser.find_element_by_id('captcha-submitCode')
        btn.click()

    def click_login_button(self):
        btn = self.browser.find_element_by_id('loginbutton')
        if btn:
            btn.click()
            self.proxy.wait_for_traffic_to_stop(3, 60)
        else:
            logging.error("failed to find login button")

    def produce_result(self):
        """
        get cookie from selenium or proxy and get login content
        :return:
        """
        return self.browser.get_cookies(), self.browser.page_source

    def check_har_1(self, har):
        login = False
        url = None
        for entry in har.get('log', {}).get('entries', []):
            if entry['request']['url'] in ["https://rd2.zhaopin.com/s/homepage.asp",
                                           "https://ihr.zhaopin.com/loginTran.do"]:
                url = entry['request']['url']
                login = True
                break
        return login, url

    def _hack_do(self, account, captcha_resolver):
        start = int(time.time() * 1000)
        self.account = account
        self.init_hacker()
        if not self.request_index():
            logging.warning("failed to fetch index with selenium")
            return None, None
        self.fill_in_form()
        cap = self.get_captcha()
        if cap is None:
            return None, None
        self.simulate_verify(captcha_resolver(cap))
        self.proxy.new_har()
        self.click_login_button()
        login_source = self.browser.page_source
        # save_file(login_source, "src_" + self.account['u'] + '_.txt', mode='w')
        time.sleep(1)
        # save_file(login_source, "src_2_" + self.account['u'] + '_.txt', mode='w')
        cookies, src = self.produce_result()
        end = int(time.time() * 1000)
        # save_file(src, "src_3_" + self.account['u'] + '_.txt', mode='w')
        har = self.proxy.har
        # save_file(json.dumps(har, indent=4), '2har_' + self.account['u'] + '.json', mode='w')
        # save_file(json.dumps(cookies, indent=4), 'cookies_' + self.account['u'] + '.json', mode='w')
        is_login, url = self.check_har_1(har)
        logging.debug("login result: %s, %s", is_login, url)

        return is_login, url, end - start, cookies

    def hack(self, account, captcha_resolver):
        if is_osx():
            return self._hack_do(account, captcha_resolver)
        with Xvfb():
            return self._hack_do(account, captcha_resolver)

    def __hack2_do(self, account, captcha_resolver):
        start = int(time.time() * 1000)
        self.account = account
        self.init_hacker()
        if not self.request_index():
            logging.warning("failed to fetch index with selenium")
            return None, None
        self.fill_in_form()
        cap = self.get_captcha()
        if cap is None:
            return None, None
        self.simulate_verify(captcha_resolver(cap))
        self.proxy.new_har()
        self.click_login_button()
        login_source = self.browser.page_source
        # save_file(login_source, "src_" + self.account['u'] + '_.txt', mode='w')
        time.sleep(1)
        # save_file(login_source, "src_2_" + self.account['u'] + '_.txt', mode='w')
        cookies, src = self.produce_result()
        end = int(time.time() * 1000)
        # save_file(src, "src_3_" + self.account['u'] + '_.txt', mode='w')
        har = self.proxy.har
        # save_file(json.dumps(har, indent=4), '2har_' + self.account['u'] + '.json', mode='w')
        # save_file(json.dumps(cookies, indent=4), 'cookies_' + self.account['u'] + '.json', mode='w')
        is_login, url = self.check_har_1(har)
        logging.debug("login result: %s, %s", is_login, url)

        return cookies, login_source

    def hack2(self, account, captcha_resolver):
        if is_osx():
            return self.__hack2_do(account, captcha_resolver)
        with Xvfb():
            return self.__hack2_do(account, captcha_resolver)

    def _do_check_can_search(self, url, checker=None):
        self.init_hacker()
        self.proxy.new_har(options={"captureContent": True})
        self.browser.get(url)
        time.sleep(4)
        har = self.proxy.har
        for entry in har.get('log', {}).get('entries', []):
            if entry.get('request', {}).get('url') == url and entry.get(
                    'response', {}).get('status') == 200:
                return checker(entry.get('response', {}).get('content', {}).get('text')) if checker else True
        return False

    def check_can_search(self, url, checker=None):
        if is_osx():
            return self._do_check_can_search(url, checker)
        with Xvfb():
            return self._do_check_can_search(url, checker)

    def close(self):
        if self.browser:
            try:
                self.browser.close()
                self.browser = None
            except:
                pass
        if self.proxy:
            self.proxy.close()
            self.proxy = None
        if self.proxy_server:
            try:
                self.proxy_server.stop()
            except Exception as e:
                logging.exception(e)
            self.proxy_server = None