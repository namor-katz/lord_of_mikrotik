#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def create_mit_name(text):
    a = text.strip() #this is make in function on bot
    b = re.sub(r'\s+',  ' ',  a)
    c = b.split(' ')
    duration = 3600
    vpn_name = ' '
    for i in c:
        if i.isdigit() == True:
            duration = i
        else:
            vpn_name = i
    return vpn_name,  duration
