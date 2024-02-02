#!/usr/bin/env python
# -*- coding: utf8 -*-
from hikyuu.interactive import *
from tools.Ashare import *
import time
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

# STOCKTYPE_BLOCK 股票类型-板块
# STOCKTYPE_A 股票类型-A股
# STOCKTYPE_INDEX 股票类型-指数
# STOCKTYPE_B 股票类型-B股
# STOCKTYPE_FUND 股票类型-基金
# STOCKTYPE_ETF 股票类型-ETF
# STOCKTYPE_ND 股票类型-国债
# STOCKTYPE_BOND 股票类型-其他债券
# STOCKTYPE_GEM 股票类型-创业板
# STOCKTYPE_START 股票类型-创业板
# STOCKTYPE_TMP 股票类型-临时CSV

timestamp = datetime.now().strftime("%Y%m%d")
filename = f'/root/data/filter_{timestamp}.json'
stable = {}

# 打开并加载json文件
if os.path.exists(filename):
    with open(filename, 'r') as f:
        print(f.read())
        data = json.load(f) if f.read().strip() else {}
else:
    data = {}

for stock in sm:
    # Your code here
    if stock.type !=  constant.STOCKTYPE_A:
        continue
    if stock.market == 'BJ':
        continue
    
    kdata = stock.get_kdata(Query(-500))
    a = VOL(kdata)
    MA3 = MA(a, 3)
    MA5 = MA(a, 5)
    MA10 = MA(a, 10)
    MA30 = MA(a, 30)
    MA125 = MA(a, 125)
    MA250 = MA(a, 250)
    
    if len(kdata) < 30:
        continue

    v = kdata[-2]
    vc = kdata[-1]
    print(vc)

    ma3c = 2*MA3.get_by_datetime(v.datetime)
    ma5c = 2*MA5.get_by_datetime(v.datetime)
    ma10c = 2*MA10.get_by_datetime(v.datetime)
    ma30c = 2*MA30.get_by_datetime(v.datetime)
    ma125c = 2*MA125.get_by_datetime(v.datetime)
    ma250c = 2*MA250.get_by_datetime(v.datetime)
    vol2c = 2*a.get_by_datetime(v.datetime)
    numbers = [ma3c, ma5c, ma10c, ma30c, ma125c, ma250c, vol2c]
    max_value = max(numbers)
    min_value = min(numbers)
    
    end = kdata.get_pos_in_stock(v.datetime)
    start125 = end - 125 if end - 125 > 0 else 0
    list125 = stock.get_krecord_list(Query(start=start125, end=end))

    # 百分之十半年线
    count = 0
    for element in list125:
        if element.volume > min_value * 2:
            count += 1
    percentage = count / len(list125) * 100
    if percentage < 10:
        # print(numbers)
        # print(v.datetime)
        # if vc.close > v.close * 1.06 and vc.volume > max_value :
        if vc.close > v.close * 1.06 and vc.close < v.close * 1.09 and  vc.volume > max_value :
            # print(v)
            # print(vc)
            # print('买入', stock.market + stock.code, vc.close, v.close, vc.volume, max_value, vc)
            # stable[stock.market + stock.code]=(stock.market + stock.code, v.datetime, v.close, min_value, max_value)
            stock_key = stock.market + stock.code
            if stock_key not in data:
                data[stock_key] = stock_key

        # if vc.close > v.close * 1.09 and vc.volume > max_value:
            # print('涨停', stock.market + stock.code, vc.close, v.close, vc.volume, max_value, vc)
print(data)
with open(filename, 'w') as f:
    json.dump(data, f)

print("============ Dump filter result OK! ============")