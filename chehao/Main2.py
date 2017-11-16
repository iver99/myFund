# -*- coding: utf-8 -*-
import urllib.request, socket, re, sys, os
from urllib import request
from bs4 import BeautifulSoup as bs

# 保存首页的图片到本地
# 定义文件保存路径
targetPath = "d:\\myfund.txt"

def getFundInfo(map):
    # iterate each fund info
    for key, value in map.items():
        fund_key = key
        fund_resp = request.urlopen(value)
        fund_data_html = fund_resp.read().decode('utf-8')
        soup = bs(fund_data_html, 'html.parser')
        num_ui = soup.find_all('span', class_=['ui-font-middle','ui-num'])
        for item in num_ui:
            try:
                if item.find_previous('span').get_text().index('近1月') >=0:
                    print(key)
                    print('近一月: ', item.string)
                else:
                    print(item.find_previous('span').string)
            except ValueError:
                continue

            # print(item.string)
        # tmp = soup.find(text = "近1月").find_parent().find_next_sibling()
        # print(tmp.string)
        # print(key)
        # print(num_ui[1].string)


def getFundList(map, url):
    resp = request.urlopen(url)
    html_data = resp.read().decode('gbk')
    soup = bs(html_data, 'html.parser')
    num_boxes = soup.find_all('div', class_='num_box')
    # TODO: handle fund start with '0' first
    fund_list = num_boxes[0].find_all('li')
    for item in fund_list:
        # 有三个<a>,只要第一个, ex:（092002）大成债券C | 基金吧 | 档案
        specific_fund = item.find_all('a')
        # fileHandle.write(specific_fund[0]['href'] + '\n')
        # fileHandle.write(specific_fund[0].string + '\n')
        if len(specific_fund):
            # print(specific_fund[0]['href'])
            # print(specific_fund[0].string)
            map[specific_fund[0].string] = specific_fund[0]['href']
        else:
            print("*Fund list is empty!!!*")



url = "http://fund.eastmoney.com/allfund.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '                            'Chrome/51.0.2704.63 Safari/537.36'
}


def main():
    # fundMap = {}
    # for debug
    fundMap = {}
    getFundList(fundMap, url)
    getFundInfo(fundMap)

    print(fundMap)


main()
