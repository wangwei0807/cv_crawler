# coding: utf-8
import base64
import json
import os

import chardet
import requests
import time
user = 'lilian'
pwd = 'Lilian123456'
post_url = 'http://v1-http-api.jsdama.com/api.php?mod=php&act=upload'
softwareId = '7783'
softwareSecret = 'RKM936henz3OzGgpg9c8UCViQ32lCqwhO8cCOqyG',

def get_coordinate(api_username=user, api_password=pwd, image='', api_post_url=post_url,
                   yzm_min='1', yzm_max='8', yzm_type='1314', tools_token=''):
    '''
            main() 参数介绍
            api_username    （API账号）             --必须提供
            api_password    （API账号密码）         --必须提供
            file_name       （需要打码的图片路径）   --必须提供
            api_post_url    （API接口地址）         --必须提供
            yzm_min         （验证码最小值）        --可空提供
            yzm_max         （验证码最大值）        --可空提供
            yzm_type        （验证码类型）          --可空提供
            tools_token     （工具或软件token）     --可空提供

    '''
    # api_username =
    # api_password =
    # file_name = 'c:/temp/lianzhong_vcode.png'
    # api_post_url = "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload"
    # yzm_min = '1'
    # yzm_max = '8'
    # yzm_type = '1303'
    # tools_token = api_username
    file_name = os.getcwd() + '\\%d.png' % int(time.time())
    with open(file_name, 'wb+') as f:
        f.write(image)
        f.flush()
    # proxies = {'http': 'http://127.0.0.1:8888'}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
        # 'Content-Type': 'multipart/form-data; boundary=---------------------------227973204131376',
        'Connection': 'keep-alive',
        'Host': 'v1-http-api.jsdama.com',
        'Upgrade-Insecure-Requests': '1'
    }

    files = {
        'upload': (file_name, open(file_name, 'rb'), 'image/png')
    }

    data = {
        'user_name': api_username,
        'user_pw': api_password,
        'yzm_minlen': yzm_min,
        'yzm_maxlen': yzm_max,
        'yzmtype_mark': yzm_type,
        'zztool_token': tools_token,
        'upload': (file_name, open(file_name, 'rb'), 'image/png')
    }
    s = requests.session()
    r = s.post(api_post_url, headers=headers, data=data, files=files, verify=False)
    print(r.text)
    if '密码错误' in r.text or 'name or pw error' in r.text:
        return 0
    j = json.loads(r.text)
    if j.get('data', None):
        return j.get('data').get('availablePoints')
    else:
        print(r.text)
        return 0

def resolve(image, minlen=2, maxlen=20, _type=68):
    """
    识别验证码
    :param imgge: 验证码图片或文件
    :param minlen: 验证码要识别的字符的最小个数
    :param maxlen: 验证码最大个数
    :param _type: 类型,普通验证码填0，点击式验证码68，点击式验证码 maxlen,minlen放空，即maxlen='',minlen=''
    :return:
    """
    # 'brantbzhang', 'p': 'heLlo_Ipin@l234
    data = {
        'username': user,
        'password': pwd,
        'captchaMaxLength': maxlen,
        'captchaMinLength': minlen,
        'captchaType': _type,
        'softwareId': softwareId,
        'softwareSecret': softwareSecret,
        'captchaData': base64.b64encode(image).decode('utf-8')
    }
    HEADERS = {'Content-Type': 'application/json'}
    PROCESS_URL = 'https://v2-api.jsdama.com/upload'
    # files = {'upload': ('a.jpg', img)}

    # time.sleep(3)
    # print json.dumps(data, indent=4)
    # self.set_proxy('192.168.1.251:5000')
    con = requests.post(PROCESS_URL, data=json.dumps(data), headers=HEADERS)
    if con is None:
        return False
    print('====>lianzhong.result:', con.text)
    j = json.loads(con.text)
    if int(j.get('code', -1)) == 0:
        lastid = j['data']['captchaId']
        return j['data']['recognition']
    elif u"已经损坏或者不是正确的图像格式" in j.get("message", u""):
        return False
    else:
        print(json.dumps(j, indent=4))
        # raise Exception(u"联众服务返回异常数据[%s]" % con.text)
        return False

if __name__ == '__main__':
    # download_vcode()
    get_coordinate('wangwei_0807',
         '19910807Wang',
         'c:/temp/lianzhong_vcode.png',
         "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload",
         '',
         '',
         '1314',  # 坐标点击4次
         '')

    '''
        main() 参数介绍
        api_username    （API账号）             --必须提供
        api_password    （API账号密码）         --必须提供
        file_name       （需要打码的图片路径）   --必须提供
        api_post_url    （API接口地址）         --必须提供
        yzm_min         （验证码最小值）        --可空提供
        yzm_max         （验证码最大值）        --可空提供
        yzm_type        （验证码类型）          --可空提供
        tools_token     （工具或软件token）     --可空提供
    '''