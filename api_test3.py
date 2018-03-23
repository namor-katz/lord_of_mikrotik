#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_api3.py
#  
#  Copyright 2018 Roman <roman@roman-home>
#  
import ssl
from librouteros import connect
#from pprint import pprint
import os
#from datetime import datetime
from time import time

# check conf file
if os.access('config.py', os.F_OK) == True:
    import config
else:
    print('no config file! EXIT')
    print('please, create config.py, added to login, password and ip or dns  \
    your router')
    exit()

# connect to mikrotik
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ctx.set_ciphers('RSA')
api = connect(username = config.login, password = config.password, host = config.host, ssl_wrapper=ctx.wrap_socket, port=8729)


# total count user vpn
def list_count_vpn_user():
    users = api(cmd='/ppp/secret/print')
    count_users = len(users)
    return count_users


# names all users vpn
def list_vpn_user_name():
    users = api(cmd='/ppp/secret/print')
    names = []
    for i in users:
        names.append(i['name'])
    return names



#count activity user vpn
def list_count_activity_vpn_user():
    users = api(cmd='/ppp/secret/print')
    i = 0
    for name in users:
        if name['disabled'] == False:
            i = i +1
    #return i
    count = i
    return count
    

#name activity user vpn
def list_vpn_active_user():
    users = api(cmd='/ppp/secret/print')
    names = []
    for i in users:
        if i['disabled'] == False:
            names.append(i['name'])
            #print(i['name'])
        else:
            pass
    return names

#close active conection from select user
def close_connection(name_input):
    '''this function close active connect'''
    connect = api(cmd='/ppp/active/print')
    if len(connect) != 0:
        
        params = {}
        for i in connect:
            if i['name'] == name_input:
                name_id = i['.id']
                params['.id'] = name_id
                api(cmd='/ppp/active/remove', **params)
                return True
            else:
                pass
    else:
        pass
        

#disable user vpn
def disable_vpn_user(name_input):
    ''' this function disable user, if exists'''
    users = api(cmd='/ppp/secret/print')
    params = {'disabled' : True}
    for i in users:
        if i['name'] == name_input:
            name_id = i['.id']
            params['.id'] = name_id
            api(cmd='/ppp/secret/set', **params)
            result = True
            return result
        else:
            pass
            
    #!!! close session if exists
    api(cmd='/ppp/secret/set', **params)
    #api.close
    

#enable user vpn
def enable_vpn_user(name_input):
    users = api(cmd='/ppp/secret/print')
    params = {'disabled' : False, '.id' : name_input}
    for i in users:
        if i['name'] == name_input:
            name_id = i['.id']
            params['.id'] = name_id
            api(cmd='/ppp/secret/set', **params)
            #print('user enable!')
            result = True
            return result
        else:
            pass

#user vpn status
def user_vpn_status(name_input):
    pass
    
#remove user vpn 
def remove_vpn_user(name_input):
    users = api(cmd='/ppp/secret/print')
    params = {}
    
    for i in users:
        if i['name'] == name_input:
            name_id = i['.id']
            params['.id'] = name_id
            api(cmd='/ppp/secret/remove', **params)
            #print('yes! remove!!')
            remove = True
            return remove
        else:
            #print('user not exist')
            pass
    

#create user vpn
def create_vpn_user(duration=3600):
    #users = api(cmd='/ppp/secret/print')
    params = {'profile' : 'default', 'service' : 'pptp'}
    import generation_pass
    import generation_name2
    vpn_pass = generation_pass.create_password()
    vpn_name = generation_name2.create_name()
    
    params['name'] = vpn_name
    params['password'] = vpn_pass
    api(cmd='/ppp/secret/add', **params)
    #from create_database import add_user_in_database
    #add_user_in_database(vpn_name)
    from add_time import add_data
    add_data(vpn_name,  duration)
    #date_create = a[0]
    #date_off = a[1]
    from create_database import add_user_in_database
    add_user_in_database(vpn_name,  duration)
    '''
    from duration import date_off
    print(delta)
    date_off(delta)
    '''
    return params
    #!! added to database

#list profile print
def list_profile():
    profile = api(cmd='/ppp/profile/print')
    return profile
    #pprint(profile)

#list active connections
def list_active_connections():
    connections = api(cmd='/ppp/active/print')
    conn = []
    #print(type(conn))
    for i in connections:
        conn.append(i)
    #print(type(conn))
    #print(connections)
    return connections
 
#time left
def time_left(username):
     '''this function retunr left time'''
     from create_database import time_to_poweroff
     a = time_to_poweroff(username)
     if a == None:
         pass
         time_left1 = 0
         return time_left1
     else:
         date_off = a[0]
         date_real = time()
         time_left1 = date_off - int(date_real)
         print('я из апи',  time_left1)
         return time_left1
         
     
#create new profile with fixed time
