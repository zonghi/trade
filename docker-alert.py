#!/usr/bin/env python
# -*- coding: utf8 -*-
from tools.Ashare import *
from datetime import datetime
import os
import json
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

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

def send_email(data, smtp_server="smtp.qq.com", smtp_port=587, username="595652979@qq.com", password="mdfraecghcokbfhf", from_email="595652979@qq.com", to_email="595652979@qq.com"):
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "The subject of your email"

    # 将数据附加到邮件
    json_data = json.dumps(data, indent=4)
    msg.attach(MIMEText(json_data, 'plain'))

    # 发送邮件
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    print(f"============ new alert:{len(data['buy'])} Alert OK! ============")

def process_alerts():
    timestamp = datetime.now().strftime("%Y%m%d")  # 这里假设你已经定义了timestamp
    filter_filename = f'/root/data/filter_{timestamp}.json'
    alert_filename = f'/root/data/alert_{timestamp}.json'
    double = {}
    all = {}
    alert = False

    # 打开并加载json文件
    if os.path.exists(filter_filename):
        with open(filter_filename, 'r') as f:
            filter_data = json.load(f)
            print(filter_data)
    else:
        filter_data = {}

    all['new'] = {}
    all['stop'] = {}
    all['buy'] = {}
    # 打开并加载json文件
    if os.path.exists(alert_filename):
        with open(alert_filename, 'r') as f:
            data = json.load(f)
    else:
        data = all
    data['new'] = {}

    for key, value in filter_data.items():
        print(f"【Stock Name: {key}】, Value: {value}")
        df=get_price(key,frequency='1d',count=10)  #分钟线实时行情，可用'1m','5m','15m','30m','60m'
        rtdf=get_price(key,frequency='5m',count=50) 
        # 计算volume的平均值
        volume_avg = df['volume'].mean()

        # 计算今天的volume总和
        today = datetime.now().strftime("%Y-%m-%d")
        today_volume_sum = rtdf[rtdf.index.strftime("%Y-%m-%d") == today]['volume'].sum()
        print(f"Today's volume sum: {today_volume_sum}")
        
        last_vol = df.iloc[-1]['volume']
        cur_vol = today_volume_sum
        last_close = df.iloc[-1]['close']
        cur_close = rtdf.iloc[-1]['close']
        print(f"Volume Average: {volume_avg}")
        print(f"Last Volume: {last_vol}, Volume: {cur_vol}, times:{(cur_vol / last_vol):.2f}")
        print(f"Last Close: {last_close}, Close: {cur_close}, times:{((cur_close - last_close) / last_close):.2f}")
        if cur_vol > volume_avg * 2 and \
            cur_close > last_close * 1.075 and \
                cur_close < last_close * 1.095:
            double[key] = value
        else:
            continue
        
        # 报警
        if (cur_close > last_close * 1.08 and cur_close < last_close * 1.096):
            print('判断报警', last_close)
            if key not in data['buy']:
                alert = True
                data['buy'][key] = value
                data['new'][key] = value

        elif (cur_close >= last_close * 1.096):
            print('已涨停，不报警', last_close)
            all['stop'][key] = value
        time.sleep(0.5)

    # 打印json数据
    print(data)

    with open(alert_filename, 'w') as f:
        json.dump(data, f)

    if alert:
        send_email(data)

while True:
    process_alerts()
    print("============ Alert OK! ============")
    time.sleep(10)  # 每分钟检查一次
    




                    



