# -*- coding: utf-8 -*-
import logging.config
from urllib import request
from bs4 import BeautifulSoup as bs
from os import path
import threading
import time
import heapq

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger('main')

def getFundInfoRecentMonth(map, normal_fund, currency_fund_map, bond_fund_map):
    current_time = time.time()
    logger.info("#1 current time is %d" % current_time)
    logger.info("获取基金最近一月信息开始...")
    # iterate each fund info
    for key, value in map.items():
        fund_resp = request.urlopen(value)
        fund_data_html = fund_resp.read().decode('utf-8')
        soup = bs(fund_data_html, 'html.parser')
        # source: <dd><span>近1月：</span><span class="ui-font-middle  ui-num">--</span></dd>
        num_ui = soup.find_all('dd', limit=2)
        # 基金页面可能存在认购页面，导致无法解析出最近一月的收益，catch住这个ValueError然后继续
        try:
            # 正常来说第二个数据是source，所以下标取1, 正常情况下num_ui[1].text为'近1月：2.30%'，异常情况为'近1月：--'，或者其它情况
            if num_ui[1].text.count('近1月') <= 0 or num_ui[1].text.count('--'):
                logger.warn("不包含近1月或者包含其它非法格式数据 " + str(num_ui[1].contents))
                continue
            fund_recent_month = float(num_ui[1].contents[1].string[:-1])
        except ValueError as e:
            logger.warn(e)
            logger.warn("基金代码是 %s " % key)
            continue
        # 暂时丢弃最近一个月收益为小于 3% 的基金，提高效率(可以改到更大，提高后续排序效率)
        if fund_recent_month < 3.0:
            continue
        else:
            if key.count('ETF基金') > 0:
                currency_fund_map[key] = fund_recent_month
                logger.debug("ETF基金: fund key is [%s] and value is [%f] " % (key, fund_recent_month))
            elif key.count('债券') > 0:
                bond_fund_map[key] = fund_recent_month
                logger.debug("债券基金: fund key is [%s] and value is [%f] " % (key, fund_recent_month))
            else:
                normal_fund[key] = fund_recent_month
                logger.debug("普通基金: fund key is [%s] and value is [%f] " % (key, fund_recent_month))
                # FIXME fix below bug of time cost
    logger.info("#2 current time is %d" % time.time())
    logger.info("获取基金最近一月信息结束...%s took %d ms" % (threading.current_thread().name, (time.time() - current_time)))


# index is fund code start number ex: 方正富邦货币B(730103), index is 7
def getFundList(map, url, index):
    start_time = time.time();
    logger.info("开始获取基金列表,基金开头数字为 " + str(index))
    logger.debug("访问 url:" + url)
    resp = request.urlopen(url)
    html_data = resp.read().decode('gbk')
    soup = bs(html_data, 'html.parser')
    num_boxes = soup.find_all('div', class_='num_box')
    fund_list = num_boxes[index].find_all('li')
    logger.info("开始处理开头为%d的基金，页面获取基金个数为 %d" % (index, len(fund_list)))
    for item in fund_list:
        # 有三个<a>,只要第一个, ex:<a>（092002）大成债券C</a> | <a>基金吧</a> | <a>档案</a>
        specific_fund = item.find('a')
        # 爬取数据时，丢弃的种类关键字
        if specific_fund == None or specific_fund.string.count('货币') or specific_fund.string.count(
                '现金') or specific_fund.string.count('保本') or specific_fund.string.count('纯债'):
            continue
        map[specific_fund.string] = specific_fund['href']
    logger.info("结束处理开头为%d的基金，页面获取基金个数为 %d" % (index, len(map)))
    logger.info("获取基金列表结束...took %d ms" % (time.time() - start_time))


fund_url = "http://fund.eastmoney.com/allfund.html"


def target(index):
    # 货币基金 map
    currency_fund_map = {}
    # 债券基金 map
    bond_fund_map = {}
    # 普通基金map
    normal_fund_map = {}

    # 下面的map会包含键值对是"基金名字->基金对应的url地址"
    raw_fund_map = {}
    getFundList(raw_fund_map, fund_url, index)
    # 下面map会包含键值对是"基金名字->最近一月的收益"
    # normal_fund = {}
    getFundInfoRecentMonth(raw_fund_map, normal_fund_map, currency_fund_map, bond_fund_map)
    before_sort_time = time.time();
    # 对获取到的"基金名字->最近一月的收益" map进行排序，从高到低,取最高的十个
    sorted_normal_fund = heapq.nlargest(10, normal_fund_map.items(), key=lambda s: s[1])
    logger.info("普通基金最近一个月收益由高到低为：")
    logger.info(sorted_normal_fund)

    sorted_currency_fund = heapq.nlargest(10, currency_fund_map.items(), key=lambda s: s[1])
    logger.info("ETF基金最近一个月收益由高到低为：")
    logger.info(sorted_currency_fund)

    sorted_bond_fund = heapq.nlargest(10, bond_fund_map.items(), key=lambda s: s[1])
    logger.info("债券基金最近一个月收益由高到低为：")
    logger.info(sorted_bond_fund)
    logger.info("基金排序花费时间为 %d ms" % (time.time() - before_sort_time))


def main():
    logger.info("基金爬虫开始。。。")

    t1 = threading.Thread(target=target, name="Thread-1", args=(1,))
    t1.start()

    t2 = threading.Thread(target=target, name="Thread-2", args=(2,))
    t2.start()

    t3 = threading.Thread(target=target, name="Thread-3", args=(3,))
    t3.start()

    t4 = threading.Thread(target=target, name="Thread-4", args=(4,))
    t4.start()

    t5 = threading.Thread(target=target, name="Thread-5", args=(5,))
    t5.start()

    t6 = threading.Thread(target=target, name="Thread-6", args=(6,))
    t6.start()

if __name__=='__main__':
    main()
