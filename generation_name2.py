#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  generation_name2.py
#  
#  Copyright 2018 Roman <roman@roman-home>
#from generation name

from mimesis import Food
food = Food('en')

def create_name():
    a = food.drink()
    #print(a)
    return a

