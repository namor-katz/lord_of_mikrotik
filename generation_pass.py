#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  generation_pass.py
#  
#  Copyright 2018 Roman <roman@roman-home>
#  


from random import choice
from string import ascii_letters

def create_password():
    passw = ''.join(choice(ascii_letters) for i in range(12))
    #print(passw)
    return passw

#create_password()
