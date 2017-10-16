#!coding:utf8

'''
descriptions: none
author: yqq
date: 2017/10/15 14:46
'''

import os
import threading #多线程下载
import requests

from DownLoader2 import gUserAgentList
from DownLoader2 import GetRandomUserAgent


###############################

gThreadCount = 16   #设置线程数

###############################




gPostData = {"name": "tonyl", "passwd": "qb1111", "utype": "用户名", "login": "登录"}
gLoginURL = "http://yun1.szfcar.com/login/"
gLogin = requests.session()
gSession = requests.session()
gPdfURLDictList = []

def SetUserAgentList():
    with open("../txt/user-agent.txt", "r") as inFile:
        #gUserAgentList = inFile.readlines()
        while True:
            tmpLine = inFile.readline().strip()
            if len(tmpLine) == 0:  #去掉空行
                break
            gUserAgentList.append({'User-Agent' : tmpLine})

def SetLoginResponse():
    '''
    :param postData: 
    :return: 返回登录的信息, 包含了cookie
    '''

    global gSession
    gSession = requests.session()

    global gLogin
    gLogin = gSession.post(gLoginURL, data=gPostData, headers=GetRandomUserAgent())  # 发送登录信息，返回响应信息（包含cookie）



def SetPdfURLDictList(path="../doc/AllPdfURL.txt"):

    if not os.path.exists(path):
        raise ValueError

    global gPdfURLDictList
    gPdfURLDictList = []  #清空

    with open(path, "r") as inFile:
        if __name__ == '__main__':
            lineList = inFile.readlines()
            for line in lineList:
                if len(line.strip()) == 0: #空行
                    continue

                tmpSplitedList = line.split('\t')
                if len(tmpSplitedList) != 5:
                    raise ValueError

                gPdfURLDictList.append( dict(
                    areaName = tmpSplitedList[0].strip(),
                    carCnName = tmpSplitedList[1].strip(),
                    carEnName = tmpSplitedList[2].strip(),
                    verNo = tmpSplitedList[3].strip(),
                    pdfURL = tmpSplitedList[4].strip(),
                ))

    pass


def DownloadPdf( inPdfURLDict):
    '''
    :param pdfURL: pdf的URL
    :return: 无
    '''
    pdfURL = inPdfURLDict.get("pdfURL")
    areaDir = inPdfURLDict.get("areaName").decode('utf-8')
    carDir = (inPdfURLDict.get("carCnName")+ '('+ inPdfURLDict.get("carEnName") + ')').decode('utf-8')
    verNo = inPdfURLDict.get("verNo")

    print(pdfURL)
    print(areaDir)
    print(carDir)
    tmpUerAgent = GetRandomUserAgent()

    #如果直接以版本号命名的话,直接判断"版本号.pdf"文件是否存在即可;如果存在,就不再下载
    if os.path.exists(u"../doc/tmp/{0}/{1}/{2}.pdf".format(areaDir, carDir, verNo)):
        return

    #如果此文件已经下载,则跳过
    if os.path.exists(u"../doc/tmp/{0}/{1}".format(areaDir, carDir)):
        for fileName in os.listdir(u"../doc/tmp/{0}/{1}".format(areaDir, carDir)):
            if verNo in fileName:
                return

    try:
        response = gSession.get(pdfURL, cookies=gLogin.cookies, headers=tmpUerAgent)
    except:
        with open("../doc/errorLog.txt", "a+") as errorLogFile:
            errorLogFile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(
	            inPdfURLDict.get("areaName"),
                inPdfURLDict.get("carCnName"),
                inPdfURLDict.get("carEnName"),
                inPdfURLDict.get("verNo"),
                inPdfURLDict.get("pdfURL"),
            ))
        print("ERROR:{0}".format(pdfURL))
        return

    tmpStr = response.headers.get('Content-Disposition')
    if not isinstance(tmpStr, str):
        print(response.content)
        #print(pdfURL)
        #print(tmpUerAgent)
        #raise ValueError
        response.close()
        return

    fileName = tmpStr[tmpStr.find('=') + 1:]

    #if not os.path.exists(u"../doc/tmp/{0}".format(areaDir)):
    #    os.mkdir(u"../doc/tmp/{0}".format(areaDir))
    if not os.path.exists(u"../doc/tmp/{0}/{1}".format(areaDir, carDir)):
        os.makedirs(u"../doc/tmp/{0}/{1}".format(areaDir, carDir))

    with open(u"../doc/tmp/{0}/{1}/{2}".format(areaDir, carDir, "("+verNo+")"+fileName), "wb") as outFile:   #必须是二进制模式
        outFile.writelines(response.content)
        response.close()

    pass

def DownloadInRange(beginIndex, count):
    '''
    下载[beginIndex, endIndex] 范围的功能表, 包含两端
    :param beginIndex: 
    :param endIndex: 
    :return: 
    '''

    for i in range(count):
        DownloadPdf(gPdfURLDictList[i + beginIndex])
    pass



def JobDistribute(beginIndex , jobCount ):
    '''
    :param jobCount: 任务数
    :return: 
    '''
    averageJobCount = jobCount / gThreadCount

    threadPool = []
    for i in range(gThreadCount):
        if i+1 == gThreadCount:  #最后一个线程收尾
            tmpThread = threading.Thread(target=DownloadInRange,
                                         args=(beginIndex + i*averageJobCount,
                                               jobCount - i*averageJobCount)
                                         )
        else:
            tmpThread = threading.Thread(target=DownloadInRange,
                                     args=(beginIndex + i*averageJobCount,
                                           averageJobCount)
                                         )
        threadPool.append(tmpThread)

    for thread in threadPool:  #启动所有子线程
        thread.start()

    for thread in threadPool:   #等待所有子线程结束
        thread.join()

    print("DONE!")

    pass



def main():

    SetUserAgentList()
    SetLoginResponse()
    SetPdfURLDictList()

    JobDistribute(0, len(gPdfURLDictList)) #全部下载
    #JobDistribute(3059, 3340-3059) #美国区域
    #JobDistribute(0, 11) #下载


    #再次尝试下载之前失败的
    SetPdfURLDictList("../doc/errorLog.txt")
    JobDistribute(0, len(gPdfURLDictList))


    pass

if __name__ == '__main__':

    main()
