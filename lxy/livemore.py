#!/usr/bin/env python
# -*- coding: utf8 -*-

import pandas as pd
import logging

# Define the state machine with six states
state_machine = {
    0: '上升趋势',
    1: '下降趋势',
    2: '自然上升',
    3: '自然下降',
    4: '次级上升',
    5: '次级下降'
}



logging.basicConfig(level=logging.DEBUG)

class livemore:
    def __init__(self, data):
        self.data = data
        # Set the initial state to '下降趋势'
        self.current_state = 1
        # Set the variables for the maximum values of each state
        self.max_up = 0  # 上升趋势最大值
        self.min_down = 0  # 下降趋势最小值
        self.max_natrl_up = 0  # 自然上升最大值
        self.min_natrl_down = 0  # 自然下降最小值

        self.up_line = 0
        self.down_line = 0  # 下降趋势最小值
        self.natrl_up_line = 0  # 自然上升最大值
        self.natrl_down_line = 0  # 自然下降最小值

        self.df = pd.DataFrame(columns=['price', 'current_state'])

    # ret_df = pd.DataFrame(columns=['time', 'state', 'state_name', 'price', 'up_line', 'down_line', 'natrl_up_line', 'natrl_down_line'])

    # 代码逻辑：
    # 1.正处于趋势区（上升/下降 趋势）。那么6点反转
    # 2.正处于自然区
    #     2.1 自然区突破：自然区如果超过同向的趋势区划线，或者超过自然区划线的3点，那么重新进入趋势区
    #     2.2 自然区反转：自然区反向6点进入反转。自然区如果反转，那么进入次级区
    # 3.正处于次级区（防止进入自然区后再反转，影响自然区划线）
    #     3.1 次级去如果超过同向划线，进入同向自然区
    #     3.2 次级区如果超过反向划线，进入反向自然区
    def livemoreProcess(self):

        for index, row in self.data.iterrows():
            time = index
            price = row['close']
            # Iterate over the closing prices
            # for price in closing_prices:
            # Perform state transition based on the current state and closing price
            if self.current_state == 0:
                # 上升趋势
                # Perform actions for 上升趋势 state
                if self.max_up == 0 or price > self.max_up:
                    self.max_up = price
                # 趋势反转6点认为趋势结束，进入自然区间
                if price < self.max_up * (1 - 0.066):
                    # logging.info("上升趋势->自然下降|六点反转|[最高点:" + str(round(self.max_up,2)) + "][最高点六分位:" + str(round(self.max_up * (1 - 0.066), 2)) + " 当前价格:" + str(round(price, 2)) + "]" )
                    self.up_line = self.max_up
                    self.current_state = 3
                    self.max_up = 0
                pass
            elif self.current_state == 1:
                # 下降趋势
                # Perform actions for 下降趋势 state
                if self.min_down == 0 or price < self.min_down:
                    self.min_down = price

                # 趋势反转6点认为趋势结束，进入自然区间
                if price > self.min_down * (1 + 0.066):
                    # logging.info("下降趋势->自然上升|六点反转|[最低点:" + str(round(self.min_down, 2)) + "][最低六分位:" + str(round(self.min_down * (1 + 0.066), 2)) + "][当前价格:" + str(round(price,2)) + "]")
                    self.down_line = self.min_down
                    self.current_state = 2
                    self.min_down = 0
                pass
            elif self.current_state == 2:
                # 自然上升
                # Perform actions for 自然上升 state
                if self.max_natrl_up == 0 or price > self.max_natrl_up:
                    self.max_natrl_up = price

                # 自然区价格超过趋势最值，认为重新进入趋势
                if (self.up_line != 0 and price > self.up_line) or \
                    (self.down_line != 0 and price > self.down_line * (1 + 0.033)):
                    # logging.info("自然上升->上升趋势|三点突破|[趋势高点:" + str(round(self.up_line, 2)) + "][自然高点:" + str(round(self.down_line, 2)) + "][自然高点三分位:" + str(round(self.down_line * (1 + 0.033))) + "][当前价格:" + str(round(price,2)) + "]")
                    self.current_state = 0
                    self.down_line = price
                    self.max_natrl_up = 0

                # 自然区反转，进入次级
                elif price < self.max_natrl_up * (1 - 0.066):
                    # logging.info("自然上升->次级下降|六点转向|[最高点:" + str(round(self.max_natrl_up, 2)) + "][最高点六分位:" + str(round(self.max_natrl_up * (1 - 0.066), 2)) + "][当前价格:" + str(round(price, 2)) + "]")
                    self.current_state = 5
                    self.down_line = price
                    self.max_natrl_up = 0

                pass
            elif self.current_state == 3:
                # 自然下降
                # Perform actions for 自然下降 state
                if self.min_natrl_down == 0 or price < self.min_natrl_down:
                    self.min_natrl_down = price

                # 自然区价格超过趋势最值，认为重新进入趋势
                if (self.down_line != 0 and price < self.down_line) or \
                    (self.natrl_down_line != 0 and price < self.natrl_down_line * (1 - 0.033)):
                    # logging.info("自然下降->下降趋势|三点突破|[趋势低点:" + str(round(self.down_line, 2)) + "][自然低点:" + str(round(self.natrl_down_line, 2)) + "][自然低点三分位:" + str(round(self.natrl_down_line * (1 - 0.033))) + "][当前价格:" + str(round(price,2)) + "]")
                    self.current_state = 1
                    self.natrl_down_line = price
                    self.min_natrl_down = 0
                    continue

                # 自然区反转，进入次级
                elif price > self.min_natrl_down * (1 + 0.066):
                    # logging.info("自然下降->次级上升|六点转向|[最低点:" + str(round(self.min_natrl_down, 2)) + "][最低点六分位:" + str(round(self.min_natrl_down * (1 + 0.066), 2)) + "][当前价格:" + str(round(price, 2)) + "]")
                    self.current_state = 4
                    self.natrl_down_line = price
                    self.min_natrl_down = 0

                pass

            elif self.current_state == 4:
                # 次级上升

                # 回归自然下降
                if price < self.natrl_down_line:
                    # logging.info("次级上升->自然下降||[自然下降低点:" + str(round(self.natrl_down_line, 2)) + "][当前价格:" + str(round(price, 2)) + "]")
                    self.current_state = 3
                    continue
                # 回归自然上升
                if self.down_line == 0 or price > self.down_line:
                    # logging.info("次级上升->自然上升||[自然上升高点:" + str(round(self.down_line, 2)) + "][当前价格:" + str(round(price, 2)) + "]")
                    self.current_state = 2
                    continue
                pass
            elif self.current_state == 5:
                # 次级下降

                # 回归自然上升
                if price > self.down_line:
                    # logging.info("次级下降->自然上升||[自然上升高点:" + str(round(self.down_line, 2)) + "][当前价格:" + str(round(price, 2)) + "]")
                    self.current_state = 2
                    continue
                # 回归自然下降
                if self.natrl_down_line == 0 or price < self.natrl_down_line:
                    # logging.info("次级下降->自然下降||[自然下降低点:" + str(round(self.natrl_down_line, 2)) + "][当前价格:" + str(round(price, 2)) + "]")
                    self.current_state = 3
                    continue
                pass

            # logging.info('price:' + str(round(price, 2)) + '\t time:' + str(time) + '  stat:' + str(state_machine[self.current_state]))
            self.df.loc[time] = [price, int(self.current_state)]
