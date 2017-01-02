# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-1-2 下午3:43
# @Author  : JinTian
# @Site    : 
# @File    : spiderscript.py
# @Software: PyCharm Community Edition
"""
Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    get_train_tickets.py -[gd] beijing shanghai 2017-01-25
"""
from docopt import docopt
import requests
import json
from pprint import pprint
from prettytable import PrettyTable
import datetime
from datetime import timedelta


def cli():
    """
    command line interface
    :return:
    """
    arguments = docopt(__doc__)
    from_station = convert_city_to_code(arguments['<from>'])
    to_station = convert_city_to_code(arguments['<to>'])
    if not from_station:
        print('Departure wrong, no such station.')
    elif not to_station:
        print('Destination wrong, no such station.')
    else:
        date = arguments['<date>']
        url = ('https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date={0}&leftTicketDTO.'
               'from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'.format(date, from_station,
                                                                                          to_station))
        print(url)
        print(arguments)

        r = requests.get(url, verify=False)
        status = r.json()['status']
        data = r.json()['data']
        if status:
            trains = TrainCollection(data)
            trains.pretty_print()
        else:
            print('Request failed. Please check internet connect.')


class TrainCollection(object):
    # 显示车次、出发/到达站、 出发/到达时间、历时、一等坐、二等坐、软卧、硬卧、硬座

    header = ['\33[30;42m Train', 'Station', 'Time', 'Duration', 'First',
              'Second', 'SoftSleep', 'HardSleep', 'HardSit \33[0m']

    def __init__(self, rows):
        self.rows = rows

    def __get_duration(self, row):
        """
        Get train time
        :param row:
        :return:
        """
        duration = row.get('lishi').replace(':', 'h') + 'm'
        # if duration.startswitch('00'):
        #     return duration[4:]
        # if duration.startswitch('0'):
        #     return duration[1:]
        return duration

    @property
    def trains(self):
        for row in self.rows:
            left_new_dto = row['queryLeftNewDTO']
            train = [
                # 车次
                '\33[32;41m' + left_new_dto['station_train_code'] + '\33[0m',
                # 出发、到达站
                '\n'.join(['\33[32;41m' + left_new_dto['from_station_name'] + '\33[0m',
                           '\33[31;42m' + left_new_dto['to_station_name'] + '\33[0m']),
                # 出发、到达时间
                '\n'.join([left_new_dto['start_time'], left_new_dto['arrive_time']]),
                # 历时
                self.__get_duration(left_new_dto),
                # 一等坐
                left_new_dto['zy_num'],
                # 二等坐
                left_new_dto['ze_num'],
                # 软卧
                left_new_dto['rw_num'],
                # 软坐
                left_new_dto['yw_num'],
                # 硬坐
                left_new_dto['yz_num']
            ]
            yield train

    def pretty_print(self):
        """
        Format data and pretty print out
        :return:
        """
        pt = PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)
        print('All available tickets shows above.')

    def check_available_trains(self):
        """
        Get available trains.
        :return:
        """
        for train in self.trains:
            if train[5] != '无' and train[5] != '--':
                print('Find a ticket of GaoTie! Information: {0} {1} {2} {3}'.format(
                    train[0], train[2], train[3], train[5]
                ))
                print(train)
            elif train[8] != '无' and train[8] != '--':
                print('Find a ticket of GaoTie! Information: {0} {1} {2} {3}'.format(
                    train[0], train[2], train[3], train[5]
                ))
                print(train)
            else:
                print('Sorry, can not find now, I will try again later.')






def convert_city_to_code(c):
    city_code_dict = {}
    with open('city_code.txt', 'r+') as f:
        for l in f.readlines():
            city = l.split(':')[0]
            code = l.split(':')[1].strip()
            city_code_dict[city] = code
    try:
        return city_code_dict[c]
    except KeyError:
        return False


def find_available_train():
    arguments = docopt(__doc__)
    from_station = convert_city_to_code(arguments['<from>'])
    to_station = convert_city_to_code(arguments['<to>'])
    date_str = arguments['<date>']
    date_date = str_to_date(date_str)
    today = datetime.datetime.today()
    date_earliest = date_date - timedelta(days=3)
    if date_earliest < today:
        date_earliest = today
        print('\33[30;42m --------Start Autopilot Check Available Tickets.--------- \33[0m')
        for i in range(1, 10):
            date_next = date_earliest + timedelta(days=1)
            date_earliest = date_next
            date_next_str = date_to_str(date_next)
            from_station = convert_city_to_code(arguments['<from>'])
            to_station = convert_city_to_code(arguments['<to>'])
            if not from_station:
                print('Departure wrong, no such station.')
            elif not to_station:
                print('Destination wrong, no such station.')
            else:
                url = ('https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date={0}&leftTicketDTO.'
                       'from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'.format(date_next_str,
                                                                                                  from_station,
                                                                                                  to_station))

                print('\33[32;41m Check the {0} day on {1} from {2} to {3} \33[0m'.format(i, date_next_str,
                                                                                          from_station, to_station))
                r = requests.get(url, verify=False)
                status = r.json()['status']
                data = r.json()['data']
                if status:
                    all_available_trains = []
                    trains = TrainCollection(data)
                    for train in trains:
                        print(train)
                else:
                    print('Request failed. Please check internet connect.')
    else:
        print('\33[30;42m --------Start Autopilot Check Available Tickets.--------- \33[0m')
        for i in range(1, 10):
            date_next = date_earliest + timedelta(days=1)
            date_earliest = date_next
            date_next_str = date_to_str(date_next)
            from_station = convert_city_to_code(arguments['<from>'])
            to_station = convert_city_to_code(arguments['<to>'])
            if not from_station:
                print('Departure wrong, no such station.')
            elif not to_station:
                print('Destination wrong, no such station.')
            else:
                url = ('https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date={0}&leftTicketDTO.'
                       'from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'.format(date_next_str,
                                                                                                  from_station,
                                                                                                  to_station))
                print('\33[37;40m Check the {0}th day on {1} from {2} to {3} \33[0m'.format(i, date_next_str,
                                                                                            from_station, to_station))
                r = requests.get(url, verify=False)
                status = r.json()['status']
                data = r.json()['data']
                if status:
                    all_available_trains = []
                    trains = TrainCollection(data)
                    trains.check_available_trains()

                else:
                    print('Request failed. Please check internet connect.')



def str_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d')


def date_to_str(date):
    return datetime.datetime.strftime(date, "%Y-%m-%d")

if __name__ == '__main__':
    # cli()
    find_available_train()
