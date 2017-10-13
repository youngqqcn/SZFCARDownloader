#!coding:utf8

'''
Date:2017/10/13/13:51
Author:yqq
Description:none
'''

# !coding:utf-8


#!coding:utf8

'''
Date:2017/10/13/14:15
Author:yqq
Description: 下载 "深圳爱夫卡网站上的功能表"
'''


import urllib

import urllib2
import requests
import re

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}


def get_xsrf():
	firstURL = "http://www.zhihu.com/#signin"
	request = urllib2.Request(firstURL, headers=headers)
	response = urllib2.urlopen(request)
	content = response.read()
	pattern = re.compile(r'name="_xsrf" value="(.*?)"/>', re.S)
	_xsrf = re.findall(pattern, content)
	return _xsrf[0]


def login(par1):
	s = requests.session()
	# afterURL = "http://yun1.szfcar.com/downcenter/"        # 想要爬取的登录后的页面
	afterURL = "http://yun1.szfcar.com/download?pdf=59155"
	loginURL = "http://yun1.szfcar.com/login/"  # POST发送到的网址
	login = s.post(loginURL, data=par1, headers=headers)  # 发送登录信息，返回响应信息（包含cookie）
	response = s.get(afterURL, cookies=login.cookies, headers=headers)  # 获得登陆后的响应信息，使用之前的cookie

	tmpStr = response.headers.get('Content-Disposition')
	fileName = tmpStr[tmpStr.find('=')+1 : ]
	print(fileName)

	with open("../doc/tmp/{0}".format(fileName), "wb") as outFile:   #必须是二进制模式
		outFile.writelines(response.content )

	return response.headers


if __name__ == "__main__":

	data = {"name": "tonyl", "passwd": "qb1111", "utype": "用户名", "login": "登录"}

	login(data)

	#outFile = open("./out.pdf", "w")
	#outFile.write(login(data))

	pass




