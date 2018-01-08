# -*- coding: utf-8 -*-
import urllib.request, socket, re, sys, os
import logging
import logging.config
import operator
from urllib import request
from bs4 import BeautifulSoup as bs
from collections import OrderedDict
from os import path
import threading
import time

# import fundutil
# 保存首页的图片到本地
# 定义文件保存路径
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
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

def getFundInfoRecentMonth(map, normal_fund, currency_fund_map, bond_fund_map):
    current_time = time.time()
    logger.info("获取基金最近一月信息开始...")
    # iterate each fund info
    for key, value in map.items():
        fund_resp = request.urlopen(value)
        fund_data_html = fund_resp.read().decode('utf-8')
        soup = bs(fund_data_html, 'html.parser')
        num_ui = soup.find_all('span', class_=['ui-font-middle', 'ui-num'])
        for item in num_ui:
            if item.find_previous('span').get_text().count('近1月') > 0:
                # print(key)
                # print(item.get_text()[:-1])
                # print(int(item.get_text()[:-1]))
                # remove the at tail'%'
                # 暂时丢弃最近一个月收益为负的基金，提高效率
                fund_recent_month = float(item.get_text()[:-1])
                if (fund_recent_month < 0):
                    continue
                else:
                    if (key.count('货币') > 0):
                        currency_fund_map[key] = fund_recent_month
                        logger.debug("货币基金: fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
                    elif (key.count('债券') > 0):
                        bond_fund_map[key] = fund_recent_month
                        logger.debug("债券基金: fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
                    else:
                        normal_fund[key] = fund_recent_month
                        logger.debug("普通基金: fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
    logger.info("获取基金最近一月信息结束...%s took %d ms" % (threading.current_thread().name, (time.time() - current_time)))


# index is fund code start number ex: 方正富邦货币B(730103), index is 7
def getFundList(map, url, index):
    start_time  = time.time();
    logger.info("获取基金列表开始...fund prefix is " + str(index))
    logger.info("访问 url:" + url)
    resp = request.urlopen(url)
    html_data = resp.read().decode('gbk')
    soup = bs(html_data, 'html.parser')
    num_boxes = soup.find_all('div', class_='num_box')
    fund_list = num_boxes[index].find_all('li')
    for item in fund_list:
        # 有三个<a>,只要第一个, ex:（092002）大成债券C | 基金吧 | 档案
        specific_fund = item.find_all('a')
        if len(specific_fund):
            map[specific_fund[0].string] = specific_fund[0]['href']
        else:
            logger.warn("基金列表为空")
    logger.info("获取基金列表结束...took %d ms" % (time.time() - start_time))


fund_url = "http://fund.eastmoney.com/allfund.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '                            'Chrome/51.0.2704.63 Safari/537.36'
}


def target(index):
    # 货币基金 map
    currency_fund_map = {}
    # 债券基金 map
    bond_fund_map = {}
    # 普通基金map
    normal_fund_map = {}

    print('当前线程名字为 %s ' % threading.current_thread().name);
    # 下面的map会包含键值对是"基金名字->基金对应的url地址"
    raw_fund_map = {}
    getFundList(raw_fund_map, fund_url, index)
    # 下面map会包含键值对是"基金名字->最近一月的收益"
    # normal_fund = {}
    getFundInfoRecentMonth(raw_fund_map, normal_fund_map, currency_fund_map, bond_fund_map)
    before_sort_time = time.time();
    # 对获取到的"基金名字->最近一月的收益" map进行排序，从高到低
    sorted_normal_fund = sorted(normal_fund_map.items(), key=lambda d: d[1], reverse=True)
    logger.info("普通基金最近一个月收益由高到低为：")
    logger.info(sorted_normal_fund)

    sorted_currency_fund = sorted(currency_fund_map.items(), key=lambda d: d[1], reverse=True)
    logger.info("货币基金最近一个月收益由高到低为：")
    logger.info(sorted_currency_fund)

    sorted_bond_fund = sorted(bond_fund_map.items(), key=lambda d: d[1], reverse=True)
    logger.info("债券基金最近一个月收益由高到低为：")
    logger.info(sorted_bond_fund)
    logger.info("基金排序花费时间为 %d ms" % (time.time() - before_sort_time))


def main():
    logger.info("Main function begin...")

    t7 = threading.Thread(target=target, name="Thread-7", args=(7,))
    t7.start()

    t6 = threading.Thread(target=target, name="Thread-6", args=(6,))
    t6.start()


main()
