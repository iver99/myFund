# -*- coding: utf-8 -*-
import urllib.request, socket, re, sys, os
import logging
import logging.config
import operator
from urllib import request
from bs4 import BeautifulSoup as bs
from collections import OrderedDict

# import fundutil
# 保存首页的图片到本地
# 定义文件保存路径
logging.config.fileConfig('util/logging.conf')
logger = logging.getLogger('main')

# def sort(map):
#     logger.info("准备开始排序...")
#     if not bool(map):
#         logger.error("Dict为空，即将返回...")
#         return
#
#     sorted_dict = OrderedDict(sorted(map.items()))
#     logger.debug(sorted_dict)
#     logger.info("排序结束")
#     return sorted_dict

def getFundInfoRecentMonth(map, result):
    logger.info("获取基金最近一月信息开始...")
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
                    # 暂时丢弃最近一个月收益为负的基金，提高效率
                    fund_recent_month = float(item.get_text()[:-1])
                    if(fund_recent_month < 0):
                        continue
                    else:
                        result[key] = fund_recent_month
                    logger.debug("fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
                else:
                    logger.warn("")
                    print(item.find_previous('span').string)
            except ValueError:
                # //TODO :fix below warn
                # logger.warn("Value Error found, ignore.")
                continue
    logger.info("获取基金最近一月信息结束...")


def getFundList(map, url):
    logger.info("获取基金列表开始...")
    logger.info("访问 url:" + url)
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
            logger.warn("基金列表为空")
    logger.info("获取基金列表结束...")


url = "http://fund.eastmoney.com/allfund.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '                            'Chrome/51.0.2704.63 Safari/537.36'
}


def main():
    logger.info("Main function begin...")
    fund_map = {}
    getFundList(fund_map, url)
    recent_month = {}
    getFundInfoRecentMonth(fund_map, recent_month)
    # sort(recent_month)
    sorted_recent_month = sorted(recent_month.items(), key=lambda d: d[1], reverse=True)
    print(sorted_recent_month)
    logger.info("最近一个月收益由高到低为：")
    logger.info(sorted_recent_month)

    logger.info("Main Function end...")


main()
