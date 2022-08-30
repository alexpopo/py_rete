#-*- coding: utf-8 -*-
#@Time     : 2022/3/30 14:32
#@Author   : popo
#@File     : sports_lottery.py
#@Software : PyCharm

import sys
from py_rete.common import WME
from py_rete.network import ReteNetwork
from py_rete.conditions import Cond
from py_rete.conditions import Filter
from py_rete.conditions import Bind
from py_rete.production import Production
from py_rete.common import V
from py_rete.conditions import AND
from py_rete.conditions import OR


class sports_lottery(object):
    def __init__(self, sl_front_area_list: list = ['11', '25', '26', '27', '33'],
                 sl_back_area_list: list = ['06', '01'],
                 rl_front_area_list: list = ['11', '25', '26', '27', '33'],
                 rl_back_area_list: list = ['01', '06']):
        self.sl_front_area_list = sl_front_area_list
        self.sl_back_area_list = sl_back_area_list
        self.rl_front_area_list = rl_front_area_list
        self.rl_back_area_list = rl_back_area_list

    def get_front_area_guessed(self):
        front_area_guessed_value = 0

        if len(self.sl_front_area_list) == 5 & len(self.rl_front_area_list) == 5:
            for rl_front_area_item in self.rl_front_area_list:
                if rl_front_area_item in self.sl_front_area_list:
                    front_area_guessed_value += 1

        return front_area_guessed_value

    def get_back_area_guessed(self):
        back_area_guessed_value = 0

        if len(self.sl_back_area_list) == 2 & len(self.rl_back_area_list) == 2:
            for rl_back_area_item in self.rl_back_area_list:
                if rl_back_area_item in self.sl_back_area_list:
                    back_area_guessed_value += 1

        return back_area_guessed_value

    def update_sl_front_area(self, ticket_front_area):
        self.sl_front_area_list = ticket_front_area

    def update_sl_back_area(self, ticket_back_area):
        self.sl_back_area_list = ticket_back_area


# 创建彩票开奖网络
run_lottery_net = ReteNetwork()
# 个人投注体彩信息
C1 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_issue_no', V('issue_serial_number'))
C2 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_time', V('lottery_valid_date'))
C3 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_front_area', V('ticket_fa_list'))
C4 = Cond(V('SPORTS_LOTTERY_ID'), 'sl_back_area', V('ticket_ba_list'))
# 开奖体彩信息
C5 = Cond('run_lottery', 'rl_issue_no', V('issue_serial_number'))
C6 = Cond('run_lottery', 'rl_time', V('lottery_valid_date'))
C7 = Cond('run_lottery', 'rl_front_area', V('rl_fa_list'))
C8 = Cond('run_lottery', 'rl_back_area', V('rl_ba_list'))

# 前区猜中'数字'个数
front_area_bind = Bind(lambda ticket_fa_list, rl_fa_list: len(set(ticket_fa_list) & set(rl_fa_list)), V('fa_guessed'))
fa_f0 = Filter(lambda fa_guessed: fa_guessed == 0)
fa_f1 = Filter(lambda fa_guessed: fa_guessed == 1)
fa_f2 = Filter(lambda fa_guessed: fa_guessed == 2)
fa_f3 = Filter(lambda fa_guessed: fa_guessed == 3)
fa_f4 = Filter(lambda fa_guessed: fa_guessed == 4)
fa_f5 = Filter(lambda fa_guessed: fa_guessed == 5)

# 后区猜中'数字'个数
back_area_bind = Bind(lambda ticket_ba_list, rl_ba_list: len(set(ticket_ba_list) & set(rl_ba_list)), V('ba_guessed'))
ba_f0 = Filter(lambda ba_guessed: ba_guessed == 0)
ba_f1 = Filter(lambda ba_guessed: ba_guessed == 1)
ba_f2 = Filter(lambda ba_guessed: ba_guessed == 2)


def run_lottery_test(net: ReteNetwork, p: Production):
    t0 = list(p.activations)[0]
    print("t0.binding[V('fa_guessed')] is", t0.binding[V('fa_guessed')])
    print("t0.binding[V('ba_guessed')] is", t0.binding[V('ba_guessed')])
    print()


def yes_or_no(question: str):
    return input(question).upper().startswith('Y')


def lottery_ticket_number_to_string(number_input, input_size: int):
    number_input_string = []
    number_input_list = number_input.split(' ', input_size)

    for item in number_input_list:
        if int(item) < 10:
            number_input_string.append('0'+str(int(item)))
        else:
            number_input_string.append(item)

    return tuple(number_input_string)


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f5, ba_f2))
def find_first_prize():
    print("中奖 : 一等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f5, ba_f1))
def find_second_prize():
    print("中奖 : 二等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f5, ba_f0))
def find_third_prize():
    print("中奖 : 三等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f4, ba_f2))
def find_fourth_prize():
    print("中奖 : 四等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f4, ba_f1))
def find_fifth_prize():
    print("中奖 : 五等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f3, ba_f2))
def find_sixth_prize():
    print("中奖 : 六等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f4, ba_f0))
def find_seventh_prize():
    print("中奖 : 七等奖")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f3, ba_f1))
def find_eighth_prize_1():
    print("中奖 : 八等奖-1")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f2, ba_f2))
def find_eighth_prize_2():
    print("中奖 : 八等奖-2")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f3, ba_f0))
def find_ninth_prize_1():
    print("中奖 : 九等奖-1")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f1, ba_f2))
def find_ninth_prize_2():
    print("中奖 : 九等奖-2")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f2, ba_f1))
def find_ninth_prize_3():
    print("中奖 : 九等奖-3")
    print(list(run_lottery_net.matches))


@Production(AND(C1, C2, C3, C4, C5, C6, C7, C8, front_area_bind, back_area_bind, fa_f0, ba_f2))
def find_ninth_prize_4():
    print("中奖 : 九等奖-4")
    print(list(run_lottery_net.matches))


run_lottery_net.add_production(find_first_prize)
run_lottery_net.add_production(find_second_prize)
run_lottery_net.add_production(find_third_prize)
run_lottery_net.add_production(find_fourth_prize)
run_lottery_net.add_production(find_fifth_prize)
run_lottery_net.add_production(find_sixth_prize)
run_lottery_net.add_production(find_seventh_prize)
run_lottery_net.add_production(find_eighth_prize_1)
run_lottery_net.add_production(find_eighth_prize_2)
run_lottery_net.add_production(find_ninth_prize_1)
run_lottery_net.add_production(find_ninth_prize_2)
run_lottery_net.add_production(find_ninth_prize_3)
run_lottery_net.add_production(find_ninth_prize_4)


wmes = [
    WME('run_lottery', 'rl_issue_no', '21105'),
    WME('run_lottery', 'rl_time', '20210911'),
    WME('run_lottery', 'rl_front_area', ('11', '25', '26', '27', '33')),
    WME('run_lottery', 'rl_back_area', ('01', '06')),
    WME('110410-498460-051153-620804', 'sl_issue_no', '21105'),
    WME('110410-498460-051153-620804', 'sl_time', '20210911'),
]

for wme in wmes:
    run_lottery_net.add_wme(wme)

wme_sl_fa = WME('110410-498460-051153-620804', 'sl_front_area', ('11', '25', '26', '27', '33'))
wme_sl_ba = WME('110410-498460-051153-620804', 'sl_back_area', ('11', '12'))

run_lottery_net.add_wme(wme_sl_fa)
run_lottery_net.add_wme(wme_sl_ba)

# 测试代码，不进后面的while循环
# run_lottery_test(run_lottery_net, find_third_prize)
# run_lottery_net.run(1)

while 1:
    ticket_front_area_input = ()
    ticket_back_area_input = ()

    print("Let's play a game of Chinese sports lottery!")
    print("You choose sports lottery number (01~35) or (01-12)")
    print("and I'll do the same.")
    front_area_input = input("35选5(11 25 26 27 33)?")
    back_area_input = input("12选2(06 01)?")

    ticket_front_area_input = lottery_ticket_number_to_string(front_area_input, 5)
    ticket_back_area_input = lottery_ticket_number_to_string(back_area_input, 2)
    print(ticket_front_area_input)
    print(ticket_back_area_input)

    run_lottery_net.remove_wme(wme_sl_fa)
    wme_sl_fa = WME('110410-498460-051153-620804', 'sl_front_area', ticket_front_area_input)
    run_lottery_net.add_wme(wme_sl_fa)

    run_lottery_net.remove_wme(wme_sl_ba)
    wme_sl_ba = WME('110410-498460-051153-620804', 'sl_back_area', ticket_back_area_input)
    run_lottery_net.add_wme(wme_sl_ba)

    run_lottery_net.run(1)

    if not yes_or_no("Play again?"):
        sys.exit()
