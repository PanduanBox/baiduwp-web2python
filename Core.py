#-*- coding:utf-8 -*-
#CREATER   :PanduanBoxTeam-NTGtech

from tkinter.constants import TRUE
import requests
import time
import random
from lxml import etree
import json
import urllib
import urllib3
import tkinter as tk
import threading
from tkinter import filedialog
import os
import configparser
import tkinter.messagebox
import pyperclip
import base64
import sys
import re
#功能性函数
def get(url,header):
    response = requests.get(url=url,headers=header, verify=False)
    return response.text

def post(url,data,header):
    response = requests.post(url=url, data=data,headers=header)
    return response.text

def post_with_cookie(url,data,header):
    #此函数返回值为[0]-html返回数据     [1]-cookie数据(PHPSESSID=l3o8b2ptd3guedaf2skicc0voa;)
    response = requests.post(url=url, data=data,headers=header)
    cookie_value = ''
    for key,value in response.cookies.items():  
        cookie_value += key + '=' + value + ';'  
    return response.text,cookie_value

def getSubstr(input,start,end):
    #php中的setsubstr    获取在input中夹在start和end中间的文本
    find_num = input.find(start)
    result = input[find_num+len(start):]
    find_end_num = result.find(end)
    result = result[:find_end_num]
    return result

def strstr(input,fn):
    #php中的strstr      获取input中fn后的所有文本
    find_num = input.find(fn)
    result = input[find_num+len(fn):]
    return result

def strstr_front(input,fn):
    #获取input中fn前的所有文本
    find_num = input.find(fn)
    result = input[:find_num]
    return result

#       MAIN CODE

def switch_type(input,dir_pool,file_pool):
    #           用于把dir和file分类
    #input                  :dir和file混杂的数据["javascript:OpenDir('/Facerig(1)','f95r','178611707','108396099','9gcrBwNsZ2dzEcJeE9AqGg','yGuRX50BRyfNK3hxYXeuc2Z5p6GKehlE','98a6fd24efafcd98df225270c4157bb2f2a16544','1624534673','076a6fe591c77f5f3f17bb6fd1ee3f19');"]
    #dir_pool               :指定的dir池
    #file_pool              :指定的file池
    for single in input:
        if strstr_front(single,'(') == 'javascript:OpenDir':
            dir_pool.append(single)
        elif strstr_front(single,'(') == 'javascript:confirmdl':
            file_pool.append(single)
    return dir_pool,file_pool

def split_get_inf(input_pool,input_type,pool_type,processed_pool):
    #           用于创建dict类型，此函数可省下大部分代码
    #input_pool              :dir与file的信息列表["javascript:OpenDir('/Facerig(1)','f95r','178611707','108396099','9gcrBwNsZ2dzEcJeE9AqGg','yGuRX50BRyfNK3hxYXeuc2Z5p6GKehlE','98a6fd24efafcd98df225270c4157bb2f2a16544','1624534673','076a6fe591c77f5f3f17bb6fd1ee3f19');"]
    #input_type              :dict中的类型
    #pool_type               :用于指示是作用于dir还是file
    #processed_pool          :输入的池，在输入数据的基础上继续添加表，确保没下载的不会消失
    for input in input_pool:
        if pool_type == 'dir':
            input = getSubstr(input,'javascript:OpenDir(',');')
            input = input.replace("\'",'').split(',')
            if DICT_VER == False:
                temp = ''            #str版
            else:
                temp = {}            #dict版
            for each_type,each_input in zip(input_type,input):    #将input[数据表]与input_type[类型表]一一对应
                if each_type == 'dir':
                    each_input = urllib.parse.quote(each_input.encode('utf-8')).replace('/','%2F')
                    #        WARN    :                            出错原因-打包的数据类似str类型的(xx=xx&yy=yy)而不是dict,特设str/dict两种解法
                #elif each_type == 'randsk':                       #若post数据出现问题，取消此注释
                #    each_input = each_input.replace('25','')
                if DICT_VER == False:
                    temp = temp + str(each_type) + '=' + str(each_input) + '&'
                else:
                    temp[each_type] = each_input                     #将表，数据组合，添加进dict //[dict版]
            if DICT_VER == False:
                temp = temp.replace(str(each_type) + '=' + str(each_input) + '&',str(each_type) + '=' + str(each_input))#去掉结尾的'&'
            processed_pool.append(temp)                           #将dict/str打包进列表，过会返回这个列表
        elif pool_type == 'file':
            if DEBUG == True:
                print('\n传入参数-梳理file\n',input,'\n')
            input = getSubstr(input,'javascript:confirmdl(',');')
            input = input.replace("\'",'').split(',')
            if DICT_VER == False:
                temp = ''             #str版
            else:
                temp = {}            #dict版
            for each_type,each_input in zip(input_type,input):     #将input[数据表]与input_type[类型表]一一对应
                if each_type == 'dir':
                    each_input = urllib.parse.quote(each_input.encode('utf-8')).replace('/','%2F')
                    #        WARN    :                            出错原因-打包的数据类似str类型的(xx=xx&yy=yy)而不是dict,特设str/dict两种解法
                #elif each_type == 'randsk':
                #    each_input = each_input.replace('25','')
                if DICT_VER == False:
                    temp = temp + str(each_type) + '=' + str(each_input) + '&'
                else:
                    temp[each_type] = each_input                       #将表，数据组合，添加进dict //[dict版]
            if DICT_VER == False:
                temp = temp.replace(str(each_type) + '=' + str(each_input) + '&',str(each_type) + '=' + str(each_input))
            processed_pool.append(temp)                            #将dict打包进列表，过会返回这个列表
    return processed_pool

def get_dir(url,input_data,header):
    global type_dir,type_file,path_pool
    #定义变量
    dir_temp = []
    file_temp = []
    Pro_dir_Temp = []
    Pro_file_Temp = []

    dir_inf = post(url,input_data,header)
    inf_get = etree.HTML(dir_inf)
    inf = inf_get.xpath(dir_info)           #xpath获取js信息
    inf_ST = switch_type(inf,dir_temp,file_temp)#分类
    inf_GI_dir = split_get_inf(inf_ST[0],type_dir,'dir',Pro_dir_Temp)#整理
    total('input_dir',inf_GI_dir)           #添加进总结池
    inf_GI_file = split_get_inf(inf_ST[1],type_file,'file',Pro_file_Temp)#同上
    path_name = getSubstr(input_data,'dir=','&')
    path_name = urllib.parse.unquote(path_name, encoding='utf-8')
    #TODO   建立文件夹，文件夹路径为path_name
    for g in inf_GI_file:
        path_pool.append(path_name)         #路径池，要求每一个文件对应一个路径
    total('input_file',inf_GI_file)         #添加进总结池
    return True

def get_download_link(url,data,header,downpath):
    global downloaded_link
    for check in downloaded_link:
        if check == data:
            return True
    downloaded_link.append(data)
    file_inf = post(url,data,header)
    inf_get = etree.HTML(file_inf)
    inf = inf_get.xpath(file_link_info)
    file_name = inf_get.xpath(file_inf_info)
    local_down_path = os.path.join(downpath.replace('/','\\'),file_name[0])
    inf = inf[0]
    #       filename变量解释:
    #[0]名称
    #[1]大小
    #[2]MD5
    #[3]上传时间
    if DEBUG == True:
        print('\n下载路径:\n',local_down_path,'\n')
        print('\n下载链接:\n',inf,'\n')
    #TODO   在这里添加下载文件的命令
    return True

def total(type,input):
    #   一个汇总函数，所有数据都聚集于此
    #type       :使用此函数的类型
    #            get-获得储存的file dir池   input_file-添加file池   question_start-开始工作的提示   question-返回工作状态
    #input      :可为''
    global processed_filePool,processed_dirPool,satuation,cookie,path_pool
    if type == 'get':
        return processed_filePool,processed_dirPool
    elif type == 'input_file':
        processed_filePool += input
        return True
    elif type == 'input_dir':
        processed_dirPool += input
    elif type == 'question_start':
        satuation = True
        return satuation
    elif type == 'question_end':
        satuation = False
        return satuation
    elif type == 'question':
        if satuation:
            return satuation
        else:
            satuation = False
            return satuation
    elif type == 'cookie_input':
        cookie = input
    elif type == 'cookie_get':
        return cookie
    

def view_dir():
    global processed_dirPool
    for single_pro_dir in processed_dirPool:
        if DEBUG == True:
            print('\n循环中的dir池:\n',processed_dirPool,'\n')
        header = {
            'method': 'POST',
            'path': '/',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'content-length': '278',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"91\, "Chromium\";v=\"91\"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'cookie':total('cookie_get',''),
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54',
        }
        get_dir(url,single_pro_dir,header)
    total('question_end','')
    return True

def d_file():
    global processed_filePool
    global path_pool
    while total('question','') != False:
        for single_pro_file,path_single in zip(processed_filePool,path_pool):
            if DEBUG == True:
                print('\n循环中的file池:\n',processed_filePool,'\n')
            header = {
                'method': 'POST',
                'path': '/?download',
                'scheme': 'https',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'cache-control': 'max-age=0',
                'content-length': '278',
                'content-type': 'application/x-www-form-urlencoded',
                'sec-ch-ua': '\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"91\, "Chromium\";v=\"91\"',
                'sec-ch-ua-mobile': '?0',
                'sec-fetch-dest': 'iframe',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'cookie':total('cookie_get',''),
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54',
            }
            url_Dl = url + '?download'
            get_download_link(url_Dl,single_pro_file,header,path_single)

def start(surl,pwd):
    data = {
        'surl':surl,
        'pwd':pwd,
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.514.1919.810 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'path':'/'
    }
    result = post_with_cookie(url,data,header)
    total('cookie_input',result[1])
    if DEBUG == True:
        print('\n获取到的cookie:\n',result[1],'\n')
    result_html = etree.HTML(result[0])
    #print(result)
    result = result_html.xpath(dir_info)
    return result

def main_threading(surl,pwd):
    global processed_dirPool,processed_filePool,satuation,cookie,path_pool,downloaded_link
    #变量区,file_pool/dir_dloor为未处理过的数据(javascript:confirmdl(xxxx))
    #       processed_filePool/processed_dirPool为处理过的数据(dict/str)(xx=xx&yy=yy/{'z':'z','e':'e'})
    file_pool = []
    dir_pool = []
    processed_filePool = []
    processed_dirPool = []
    path_pool = []
    downloaded_link = []
    cookie = ''
    satuation = True
    #开始获取
    list = start(surl,pwd)
    if DEBUG == True:
        print('\n获取到的未被整理的数据[第一次]\n',list,'\n')
    dir_pool,file_pool = switch_type(list,dir_pool,file_pool)
    inf_dir_pool = split_get_inf(dir_pool,type_dir,'dir',processed_dirPool)
    inf_file_pool = split_get_inf(file_pool,type_file,'file',processed_filePool)
    if DEBUG == True:
        print('\n整理后的数据[第一次]\n',inf_dir_pool,'\n',inf_file_pool,'\n')
    total('input_file',inf_file_pool)
    total('input_dir',inf_dir_pool)
    thread_dir = threading.Thread(target = view_dir)
    thread_file = threading.Thread(target = d_file)
    thread_dir.start()
    thread_file.start()

if __name__ == '__main__':
    #设置区
    #   type_dir-按钮中传入js数据类型(可在浏览器的F12开发者选项中找到)
    #   type_file-按钮中传入js数据类型(可在浏览器的F12开发者选项中找到)
    #   dir_info-文件及文件夹数据在html中的位置
    #   file_link_info-下载链接在html中的位置
    #   file_inf_info-文件名称/MD5/大小/上传时间在html中的位置
    DEBUG = True
    DICT_VER = False
    url = 'https://xxxxxx/'#你的网站
    type_dir = ['dir','pwd','share_id','uk','surl','randsk','sign','timestamp','bdstoken']
    type_file = ['fs_id','time','sign','randsk','share_id','uk','bdstoken','filesize']
    dir_info = '/html/body/div/div/ul/li/a/@href'
    file_link_info = '/html/body/div/div/div/div/p/a/@href'
    file_inf_info = '/html/body/div/div/div/div/p/b/text()'
    #程序启动
    if DEBUG == True:
        print('！DEBUG MODE ACTIVE')
    #示例链接：链接：https://pan.baidu.com/s/151sgesGBLdlf-OBmiFKpvQ 提取码：6mvc
    surl = ''           #需要输入151sgesGBLdlf-OBmiFKpvQ
    pwd = ''            #需要输入6mvc
    main_threading(surl,pwd)


#                   函数解释
#   功能性函数
#       get
#           功能： 用于通过get的方式获取网页的html数据并返回
#           传参： url-目标网页的地址    header-请求头
#           反参： 目标网页的数据(str)

#       post
#           功能： 用于通过post的方式获取网页的html数据并返回
#           传参： url-目标网页的地址   data-post传送的数据     header-请求头
#           反参： 目标网页的数据(str)

#       post_with_cookie
#           功能： 用于通过post的方式获取网页html数据和cookie并返回
#           传参： url-目标网页的地址   data-post传送的数据     header-请求头
#           反参： (list)   [0]-目标网页的数据(str)  [1]-cookie(str)

#       getSubstr
#           功能： 获取在某一文本(str)中两文本(均为str)中夹着的文本
#           传参： input-被处理的文本(str)   start-要取的数据左边的内容     end-要取的数据右边的内容
#           反参： start和end中间的文本(str)

#       strstr
#           功能： 获取文本中某一文本后(均为str)的所有文本
#           传参： input-被处理的文本(str)  fn-要取的文本之前的文本
#           反参： fn后的文本(str)

#       strstr_front
#           功能： 获取文本中某一文本前(均为str)的所有文本
#           传参： input-被处理的文本(str)  fn-要取的文本之后的文本
#           反参： fn前的文本(str)

#   主函数
#       switch_type
#           功能： 将数据中的"javascript:OpenDir"与"javascript:confirmdl"分离
#           传参： input-传入的文本(str)     dir_pool-指定的文件夹的List     file_pool-指定的文件的List
#           反参： [0]经处理的dir_pool(List)    [1]经处理的file_pool(List)

#       split_get_inf
#           功能： 用于将一大串数据整理好
#           传参： input_pool-”一大串数据“(主键key)
#                 input_type-这串数据中各个的类型(值value)
#                 pool_type-指定input_pool中数据类型
#                       dir或file
#                 processed_pool-指定的List，处理完毕后的数据将添加进这个List中
#           反参： 处理后的processed_pool(List)

#       get_dir
#           功能： 指定每一个文件的路径(添加进path_pool)
#                 Post传入的数据并进行分类，整理为file与dir的列表，存入total函数中
#           传参： url-Post的URL    input_data-Post的data   header-Post的请求头
#           反参： 无，数据移交total函数做储存

#       get_download_link
#           功能： 根据传参获取下载路径及下载链接
#           传参： url-指定的url    data-指定的处理过的file的data    header-请求头      downpath-下载路径
#           反参： [0]下载路径(str)    [1]下载链接(str)

#       total
#           功能： 将处理完的数据存储在这里，避免过多使用global全局导致逻辑混乱
#                  可使用此函数添加/获取/修改变量
#           传参：type-如下
#                    get-返回文件List及文件夹List
#                    input_file-在文件List中添加input
#                    input_dir-在文件夹List中添加input
#                    question_start-更改dir获取状态为“运行”
#                    question_end-更改dir获取状态为“结束”
#                    question-返回dir获取状态
#                    cookie_input-储存网站cookie
#                    cookit_get-返回储存的cookie
#           反参： 同上

#       view_dir
#           功能： 根据total中的文件夹List循环获取各个文件夹的dir和File数据
#           传参： 无，由global全局变量获取
#           反参： 无，函数运行完成后会将total中dir获取状态更改为“结束”

#       d_file
#           功能： 根据total中的文件List循环获取各个文件的信息,与get_download_link函数连用
#           传参： 无，由global全局变量获取
#           反参： 无

#       strat
#           功能： 用于获取第一级文件夹数据来启动循环下载
#           传参： surl-分享链接(处理完毕后)    pwd-密码（可以为空）
#           反参： 第一级文件夹的html数据

#       main_threading
#           功能： 主线程，定义变量，修改参数，处理分享链接，启动循环线程
#           传参： surl-分享链接(未处理)    pwd-密码(可以为空)
