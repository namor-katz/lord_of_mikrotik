#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time

def add_data2(username,  duration=3600):
    date_create = time()
    date_create = int(date_create)
    date_off = date_create + duration
    return date_create,  date_off

'''
def who_poweroff():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM t WHERE date_off <= strftime('%s', 'now')")
    result = cursor.fetchall()
    return result
'''
