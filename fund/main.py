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
        num_ui = soup.find_all('span', class_=['ui-font-middle', 'ui-num'])
        for item in num_ui:
            #FIXME 尝试能否优化下面的搜索效率
            if item.find_previous('span').get_text().count('近1月') > 0:
                # 基金页面可能存在认购页面，导致无法解析出最近一月的收益，catch住这个ValueError然后继续
                try:
                    fund_recent_month = float(item.get_text()[:-1])
                except ValueError as e:
                    logger.warn(e + "基金代码是 %s " % key)
                    continue
                # 暂时丢弃最近一个月收益为小于 1% 的基金，提高效率
                if fund_recent_month < 1.0:
                    continue
                else:
                    if key.count('ETF基金') > 0:
                        currency_fund_map[key] = fund_recent_month
                        logger.debug("ETF基金: fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
                    elif key.count('债券') > 0:
                        bond_fund_map[key] = fund_recent_month
                        logger.debug("债券基金: fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
                    else:
                        normal_fund[key] = fund_recent_month
                        logger.debug("普通基金: fund key is [%s] and value is [%s] " % (key, item.get_text()[:-1]))
     # FIXME fix below bug of time cost
    logger.info("#2 current time is %d" % time.time())
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
    logger.info("开始处理开头为%d的基金，页面获取基金个数为 %d" % (index, len(fund_list)))
    for item in fund_list:
        # 有三个<a>,只要第一个, ex:<a>（092002）大成债券C</a> | <a>基金吧</a> | <a>档案</a>
        specific_fund = item.find_all('a')
        if len(specific_fund):
            #丢弃行为放到这个会效率比较高, 丢弃货币基金
            if specific_fund[0].string.count('货币') or specific_fund[0].string.count('现金'):
                continue
            map[specific_fund[0].string] = specific_fund[0]['href']
        else:
            logger.warn("基金列表为空")
    logger.info("结束处理开头为%d的基金，页面获取基金个数为 %d" % (index, len(map)))
    logger.info("获取基金列表结束...took %d ms" % (time.time() - start_time))


fund_url = "http://fund.eastmoney.com/allfund.html"
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '                            'Chrome/51.0.2704.63 Safari/537.36'
# }


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
    logger.info("Main function begin...")

    t7 = threading.Thread(target=target, name="Thread-7", args=(7,))
    t7.start()

    t6 = threading.Thread(target=target, name="Thread-6", args=(6,))
    t6.start()

    t5 = threading.Thread(target=target, name="Thread-5", args=(5,))
    t5.start()

    t4 = threading.Thread(target=target, name="Thread-4", args=(4,))
    t4.start()

    t3 = threading.Thread(target=target, name="Thread-3", args=(3,))
    t3.start()

    t2 = threading.Thread(target=target, name="Thread-2", args=(2,))
    t2.start()

    t1 = threading.Thread(target=target, name="Thread-1", args=(1,))
    t1.start()


main()
