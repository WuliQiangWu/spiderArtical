# _*_ coding:utf-8 _*_
# __author__ : 'aj'
# __date__ : '2018/8/6 上午11:16'

import requests

try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

header = {
    'host': 'www.zhihu.com',
    'referer': 'https://www.zhihu.com/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')

try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookie未能加载')


def get_xsrf():
    response = session.get('https://www.zhihu.com', headers=header)
    # print(response.text)
    session.cookies.save()
    session.cookies.load(ignore_discard=True)
    re_res = re.match('.*name="_xsrf" value="(.+?)"', response.text)
    if re_res:
        return re_res.group(1)
    else:
        return ''


def get_index():
    response = session.get('https://www.zhihu.com', headers=header)
    with open('index_page.html', 'wb') as f:
        f.write(response.text.encode('utf-8'))
    print('ok')


def is_login():
    inbox_url = 'https://www.zhihu.com/inbox'
    responst = session.get(inbox_url, headers=header, allow_redirects=False)
    if responst.status_code != 200:
        return False
    else:
        return True


def zhihu_login(account, password):
    """
    知乎登录
    :param account:
    :param password:
    :return:
    """
    if re.match("1\d{10}", account):
        print('手机号码登录')
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf': get_xsrf(),
            'phone_num': account,
            'password': password
        }
        resposnt = session.post(url=post_url, data=post_data, headers=header)
        session.cookies.save()


if __name__ == '__main__':
    is_login()
