#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sqlite3


#db = SqliteDatabase('database.sql')
#db = ('database.sql')

#table description
db = 'database.sql'

def create_db():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE vpn_user (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT,
    date_create int NOT NULL,
    date_off int NOT NULL,
    username_telegram text
    )
    ''')
    
    cursor.execute('''CREATE TABLE bot (
    id INTEGER PRIMARY KEY,
    username_telegram TEXT NOT NULL UNIQUE,
    level int NOT NULL
    )
    ''')
    conn.close()

#db file - is exists?
file_path = 'database.sql'
if os.access(file_path, os.F_OK) == True:
    pass
else:
    create_db()


#first auth
def add_admin(password, username):
    from config import bot_admin_password
    if password == bot_admin_password:
        conn = sqlite3.connect('database.sql')
        cursor = conn.cursor()
        cursor.execute("SELECT username_telegram FROM bot WHERE username_telegram = ?", (username,))
        b = cursor.fetchall()
        if len(b) == 0:
            cursor.execute("INSERT INTO bot (username_telegram, level) VALUES (?, 0)", (username, ))
            conn.commit()
            return True
        else:
            pass
            return False
    else:
        return False


#who poweroff?
def who_poweroff():
    conn = sqlite3.connect('database.sql')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM vpn_user WHERE date_off <= strftime('%s', 'now')")
    result = cursor.fetchall()
    conn.close()
    return result

#time to poweroff
def time_to_poweroff(username):
    ''' this function shows the time remaining before the trip.'''
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT date_off FROM vpn_user WHERE username = ?",  (username,  ))
    b = cursor.fetchone()
    print(b)
    print(type(b))
    return b
    
#whois?
def whois(username):
    conn = sqlite3.connect('database.sql')
    cursor = conn.cursor()
    cursor.execute("SELECT username_telegram, level FROM bot WHERE username_telegram = ?", (username,))
    results = cursor.fetchone()
    #print(results)
    #print(type(results))
    #print(type(results))
    if results == None:
        pass
        auth = False
        level = 5
        return auth,  level
    else:
        if len(results) == 0:
            auth = False
            return auth
        elif results == None:
            auth = False
            return auth
        else:
            #print(results[1])
            auth = True
            level = results[1]
            return auth, level
    conn.close

#add admin bot user
def add_admin_mikrotik(username_telegram, level):
    conn = sqlite3.connect('database.sql')
    cursor = conn.cursor()
    cursor.execute("SELECT username_telegram FROM bot WHERE username_telegram = ?", (username_telegram,))
    b = cursor.fetchall()
    if len(b) == 0:
        cursor.execute("INSERT INTO bot (username_telegram, level) VALUES (?, ?)", (username_telegram, level))
        #print(username_telegram)
        conn.commit()
        success = True
        #return success
    else:
        success = False
        pass
    conn.close

    return success

#list all admins
def list_all_admins():
    conn = sqlite3.connect('database.sql')
    cursor = conn.cursor()
    cursor.execute("SELECT username_telegram, level FROM Bot")
    results = cursor.fetchall()
    conn.close
    #print(results)
    return results

#added user name and create_data and pass in database
def add_user_in_database(name, duration=3600):
    #from duration import date_off
    from add_time import add_data2
    #off = date_off()
    data = add_data2(duration)
    date_create = data[0]
    date_off = data[1]
    
    conn = sqlite3.connect('database.sql', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vpn_user (username, date_create, date_off) VALUES (?, ?, ?)", (name, date_create, date_off))
    
    conn.commit()
    success = True
    conn.close
    return success

def user_exist(name):
    """this user name - exist?"""
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM vpn_user WHERE username = ?", (name, ))
    a = cursor.fetchone()
    conn.close()
    if a == None:
        return False
    else:
        return True

def add_time2(username,  duration):
    """this function added extra time from select user"""
    if user_exist(username) == True:
        from add_time import add_data2
        data = add_data2(duration)
        date_create = data[0]
        date_off = data[1]
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("UPDATE vpn_user SET date_create = ?, date_off = ? WHERE username = ?", (date_create, date_off, username) )
        conn.commit()
        return True
    else:
        return False
#whois(admin_id)

#delete vpn_user from database
def delete_user_from_database(name):
    """delete user from database"""
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vpn_user WHERE username = ?",  (name, ))
    cursor.fetchone()
    conn.commit()
    conn.close()
    #a = user_exist(name)
