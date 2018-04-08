#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  duration.py
#  
#  Copyright 2018 Roman <namor925@gmail.com>

from datetime import datetime, timedelta

def date_off(duration=1):
    date_create = datetime.now()
    #date_create = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    if duration == None:
        #delta = 'время не задано. задайте время.'
        pass
    elif duration == 0:
        delta = timedelta(hours=1)
    else:
        delta = timedelta(hours=duration)
    #print(delta)
    date_off = date_create + delta
    #print(date_off)
    return date_create.strftime("%Y.%m.%d %H:%M:%S"), date_off.strftime("%Y.%m.%d %H:%M:%S")
    
