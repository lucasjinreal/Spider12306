# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
testtidme
http://www.lewisjin.coding.me
~~~~~~~~~~~~~~~
This script implement by Jin Fagang.
: copyright: (c) 2017 Didi-Chuxing.
: license: Apache2.0, see LICENSE for more details.
"""
from datetime import timedelta, date
import datetime

a = '01'
today = datetime.datetime.today()
day = '2016-01-22'


def str_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d')


def date_to_str(date):
    return datetime.date.strftime(date, "%Y-%m-%d")

day_date = str_to_date(day)
print(day_date > today)
print(date_to_str(day_date))