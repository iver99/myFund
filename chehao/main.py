# -*- coding: utf-8 -*-
import urllib.request, socket, re, sys, os
import logging
import logging.config
from urllib import request
from bs4 import BeautifulSoup as bs
# import fundutil
# 保存首页的图片到本地
# 定义文件保存路径
targetPath = "d:\\myfund.txt"
logging.config.fileConfig('util/logging.conf')

def getFundInfoRecentMonth(map, result):
    # iterate each fund info
    for key, value in map.items():
        fund_resp = request.urlopen(value)
        fund_data_html = fund_resp.read().decode('utf-8')
        soup = bs(fund_data_html, 'html.parser')
        num_ui = soup.find_all('span', class_=['ui-font-middle', 'ui-num'])
        for item in num_ui:
            try:
                if item.find_previous('span').get_text().index('近1月') >= 0:
                    # print(key)
                    # print(item.get_text()[:-1])
                    # print(int(item.get_text()[:-1]))
                    # remove the at tail'%'
                    result[key] = float(item.get_text()[:-1])
                else:
                    print(item.find_previous('span').string)
            except ValueError:
                continue


def getFundList(map, url):
    resp = request.urlopen(url)
    html_data = resp.read().decode('gbk')
    soup = bs(html_data, 'html.parser')
    num_boxes = soup.find_all('div', class_='num_box')
    # TODO: 暂时先处理基金代号7开头的基金
    fund_list = num_boxes[7].find_all('li')
    for item in fund_list:
        # 有三个<a>,只要第一个, ex:（092002）大成债券C | 基金吧 | 档案
        specific_fund = item.find_all('a')
        if len(specific_fund):
            map[specific_fund[0].string] = specific_fund[0]['href']
        else:
            print("*Fund list is empty!!!*")


url = "http://fund.eastmoney.com/allfund.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '                            'Chrome/51.0.2704.63 Safari/537.36'
}


def main():
    logger = logging.getLogger('main')
    logger.info("Main function begin...")
    fund_map = {}
    getFundList(fund_map, url)
    recent_month = {}
    getFundInfoRecentMonth(fund_map, recent_month)

    print(recent_month)

    logger.info("Main Function end...")
main()
