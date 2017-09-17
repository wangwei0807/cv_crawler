#!/usr/bin/env python
# encoding: utf-8
import base64
import json

import requests


class LianzhongCaptcha(object):
    """
    普通验证码 1分/张
    汉字 2分/张
    点击（四字以内） 2分/张
    """

    PROCESS_URL = 'https://v2-api.jsdama.com/upload'
    ERROR_URL = 'https://v2-api.jsdama.com/report-error'
    LIANZHONG_SOFT_KEY = 'fpTof8NxP4FTFOTp6Tfi3ik6TxtfEOkE68nE3foK'
    LIANZHONG_SOFT_ID = '3202'
    HEADERS = {'Content-Type': 'application/json'}
    # 密保：12345
    ACCOUNTS = [{'u': 'brantbzhang', 'p': 'heLlo_Ipin@l234', 'softkey': '540d8f3db0151592cb35b6a2d73bdfa9'}]

    # ACCOUNTS = [{'u': 'wangwei0807', 'p': '583077969@qq.com', 'softkey': '540d8f3db0151592cb35b6a2d73bdfa9'}]

    def __init__(self, ac=None):
        self._username = ac['u'] if ac else self.ACCOUNTS[0]
        self._pwd = ac['p']
        self._soft_key = ac.get('softkey', '') or self.LIANZHONG_SOFT_KEY
        self._timeout = 60
        self._img_type = '3040'
        self.lastid = None
        self.session = requests.session()

    def point_check(self):
        # {'-1': '参数错误，用户名为空或密码为空', '-2': '用户不存在', '-3': '密码错误', '-4': ' 账户被锁定', '-5': ' 非法登录',
        # '-6': ' 用户点数不足，请及时充值', '-8': ' 系统维护中', '-9': ' 其他'}
        # url = "http://bbb4.hyslt.com/api.php?mod=php&act=point"
        url = "https://v2-api.jsdama.com/check-points"
        # params = {'user_name': self._username, 'user_pw': self._pwd, }
        params = {"softwareId": self.LIANZHONG_SOFT_ID, "softwareSecret": self.LIANZHONG_SOFT_KEY,
                  'username': self._username, 'password': self._pwd}
        response = self.session.post(url, data=params, files=files, headers=self.HEADERS, verify=False)
        if u'密码错误' in response.text or 'name or pw error' in response.text:
            return 0
        j = json.loads(response.text)
        if j.get('data', None):
            return j.get('data').get('availablePoints')
        else:
            print(response.text)
            return 0

    def resolve(self, img, minlen=4, maxlen=20, _type=0):
        """
        识别验证码
        :param img: 验证码图片或文件
        :param minlen: 验证码要识别的字符的最小个数
        :param maxlen: 验证码最大个数
        :param _type: 类型,普通验证码填0，点击式验证码68，点击式验证码 maxlen,minlen放空，即maxlen='',minlen=''
        :return:
        """
        data = {
            'username': self._username,
            'password': self._pwd,
            "softwareId": self.LIANZHONG_SOFT_ID, "softwareSecret": self.LIANZHONG_SOFT_KEY,
            'captchaMaxLength': maxlen,
            'captchaMinLength': minlen,
            'captchaType': _type,
            'captchaData': base64.b64encode(img)
        }
        # files = {'upload': ('a.jpg', img)}

        # time.sleep(3)
        # print json.dumps(data, indent=4)
        # self.set_proxy('192.168.1.251:5000')
        con = self.request_url(self.PROCESS_URL, post_fields=json.dumps(data), timeout=self._timeout,
                               headers=self.HEADERS)
        if con is None:
            return False
        print('====>lianzhong.result:', con.text)
        j = json.loads(con.text)
        if int(j.get('code', -1)) == 0:
            self.lastid = j['data']['captchaId']
            return j['data']['recognition']
        elif u"已经损坏或者不是正确的图像格式" in j.get("message", u""):
            return False
        else:
            print(json.dumps(j, indent=4))
            # raise Exception(u"联众服务返回异常数据[%s]" % con.text)
            return False

    def mark_last_error(self):
        if not self.lastid:
            return False
        data = {'username': self._username, 'password': self._pwd, 'captchaId': self.lastid,
                "softwareId": self.LIANZHONG_SOFT_ID, "softwareSecret": self.LIANZHONG_SOFT_KEY}
        self.request_url(self.ERROR_URL, post_fields=json.dumps(data), headers=self.HEADERS)


if __name__ == '__main__':
    a = LianzhongCaptcha()
    print("points:", a.point_check())