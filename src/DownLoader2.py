#!coding:utf8

'''
descriptions: none
author: yqq
date: 2017/10/14 21:37
'''
import re
import requests
import os
from random import randint

gUserAgent = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
}
gPostData = {"name": "tonyl", "passwd": "qb1111", "utype": "用户名", "login": "登录"}
gLoginURL = "http://yun1.szfcar.com/login/"
gLogin = requests.session()
gSession = requests.session()

gUserAgentList = []


# <tbody> </tbody>
gtbodyPattern = re.compile(r'<tbody>.*?</tbody>', re.DOTALL + re.MULTILINE)

#<tr> </tr>
gtrPattern = re.compile(r'<tr>.*?</tr>', re.DOTALL + re.MULTILINE)

# <td> </td>
gtdPattern = re.compile(r'<td.*?>(.*?)</td>', re.DOTALL )

#<a href=...></a>
ghrefPattern = re.compile(r'<a href="(.*?)".*?</a>', )


gRootURL = "http://www.szfcar.com"

gAreaURLList = [
    {"/car?m=3&cs=2":"中国车组"},
    {"/car?m=3&cs=11":"亚洲车组"},
    {"/car?m=3&cs=5":"欧洲车组"},
    {"/car?m=3&cs=3":"美国车组"},
    {"/car?m=3&cs=9":"柴油车型"},
    #"/car?m=3&amp;cs=102":"非洲车组",
]


def GetPageCount(carTypeHtml):
    '''
    获取多个页面的个数
    :param carTypeHtml: 第一页
    :return: 页面的个数
    '''

    gbPattern = re.compile(r'<b>.*?</b>', re.DOTALL + re.MULTILINE)
    subPageList = re.findall(gbPattern, carTypeHtml)
    if 'car' not in subPageList[len(subPageList) - 1]:
        pageCount = subPageList[0].count('<a href="') - 1  #减去"下一页"的链接
    else:
        pageCount = subPageList[0].count('<a href="')   #没有"下一页", 不需要减1
    return pageCount



def DealCarTypeHtml(carTypeHtml):

    '''
    :param carTypeHtml: 车型表html内容
    :return: [ {area:"区域名", cnName:"中文名", enName:"英文名", suffixURL:"链接"}, {..}, {..}]
    '''


    retCarDictList = []

    tbodyTextList = re.findall(gtbodyPattern, carTypeHtml)
    trTextList = re.findall(gtrPattern, tbodyTextList[0])[2:]

    for sectText in trTextList:
        fieldList = re.findall(gtdPattern, sectText)
        tmpHref = re.findall(ghrefPattern, fieldList[3])[0]
        tmpCarDict = dict(area = fieldList[0], cnName = fieldList[1],
                          enName = fieldList[2], suffixURL = tmpHref)
        retCarDictList.append(tmpCarDict)

    return  retCarDictList



def DealLogHtml(logHtml):
    '''
    :param logHtml: 处理升级页面获取不同版本的功能表pdf,的子URL
    :return: [{pdfNo:"", verNo:"", date:"", descText:""}, {},... ]
    '''

    retPdfDictList = []

    gpdfHrefPattern = re.compile(r'<a href="/download\?m=.*?&v=(.*?)">(.*?)\(.*?(20.*?)\).*?</a>', re.DOTALL)

    pdfNoList = re.findall(gpdfHrefPattern, logHtml)

    for eachTuple in pdfNoList:
        tmpPdfDict = dict(pdfNo=eachTuple[0], #pdf编号 , 用下载pdf
                          verNo=eachTuple[1], #版本号
                          date=eachTuple[2],  #更新日期
                          descText=""         #升级说明
                          )

        retPdfDictList.append(tmpPdfDict)
    return retPdfDictList


def SetUserAgentList():
    with open("../txt/user-agent.txt", "r") as inFile:
        #gUserAgentList = inFile.readlines()
        while True:
            tmpLine = inFile.readline().strip()
            if len(tmpLine) == 0:  #去掉空行
                break
            gUserAgentList.append({'User-Agent' : tmpLine})



def GetRandomUserAgent():
    '''
    :return: 随机获取一个UserAgent
    '''
    tmpIndex = randint(0, len(gUserAgentList)-1)
    return gUserAgentList[tmpIndex]

def SetLoginResponse():
    '''
    :param postData: 
    :return: 返回登录的信息, 包含了cookie
    '''

    global gSession
    gSession = requests.session()

    global gLogin
    gLogin = gSession.post(gLoginURL, data=gPostData, headers=GetRandomUserAgent())  # 发送登录信息，返回响应信息（包含cookie）





def GetHtml(inURL):
    '''
    :param inURL: 
    :return: 
    '''

    response =  gSession.get(inURL, cookies=gLogin.cookies, headers=GetRandomUserAgent())
    return response.content






if __name__ == "__main__":

    # SetUserAgentList() #
    #
    # SetLoginResponse()
    #
    # pdfURL = "http://yun1.szfcar.com/download?pdf=59155"
    # DownloadPdf(pdfURL, "China", "Ford", "v7.0")

    SetUserAgentList() #
    SetLoginResponse()

    outURLFile = open("../doc/AllPdfURL.txt", "w") #保存所有功能表pdf的URL

    for eachDict in gAreaURLList:

        url = eachDict.keys()[0]
        urlName = eachDict.values()[0]


        oneAreaHtml = GetHtml(gRootURL + url)
        print("<<" + urlName + ">>")
        print("长度"+ str(len(oneAreaHtml)))

        pageCount = GetPageCount(oneAreaHtml)
        #if urlName == "美国车组": pageCount = 1

        carTypeDictList = []
        if pageCount >= 1:
            for i in range(1, pageCount+1): #从第1页开始
                fullAreaURL = gRootURL + url + '&page={0}'.format(i)
                print(fullAreaURL)
                carTypeDictList.extend(DealCarTypeHtml(GetHtml(fullAreaURL)))

            print(len(carTypeDictList))

        for carTypeDict in carTypeDictList:
            #:return: [{area: "区域名", cnName: "中文名", enName: "英文名", suffixURL: "链接"},
            logURL = gRootURL + carTypeDict["suffixURL"]
            print(">>"+logURL)
            # return: [{pdfNo:"", verNo:"", date:"", descText:""}, {},... ]
            pdfDictList = DealLogHtml(GetHtml(logURL))
            #print(len(pdfDictList))
            if len(pdfDictList) > 0:
                for pdfDict in pdfDictList:
                    pdfURL = gRootURL + "/download?pdf={0}".format(pdfDict["pdfNo"])
                    print(">>>"+ pdfURL)
                    outURLFile.write(carTypeDict["area"]+"\t"+      #区域
                                 carTypeDict["cnName"]+"\t"+    #中文车型名
                                 carTypeDict["enName"]+"\t" +   #英文车型名
                                 pdfDict["verNo"]+"\t"+         #版本号
                                 pdfURL + "\n")                 #功能表pdf的链接

    outURLFile.close()
    pass
