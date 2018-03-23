#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  generation_name.py
#
#  Copyright 2018 Roman <roman@roman-home>
#test bot from my mikrotik

import telebot
import config
from telebot import types
import logging
import api_test3
from create_database import whois
import re
import flask
from time  import sleep

#loggin in console
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

#set environment from web hooks
WEBHOOK_HOST = '138.201.174.71'
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'webhook_key.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

app = flask.Flask(__name__)

#Empty webserver index, return nothing, just http 200
@app.route('/',  methods=['GET',  'HEAD'])
def index():
    return ''
    
# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# event handling from keyboard
text_help = '/count - количество юзеров, всего; \n /count_activ - активных юзеров; \n \
/list - показать имена всех; \n /list_a - показать имена активных; \n /create - создать нового юзера \n \
/disable - запретить юзера; \n /delete - удалить юзера'

text_no_id = 'увы, я тебя не знаю.'

@bot.message_handler(commands=['help'])
def help_for_bot(message):
    #markup = types.InlineKeyboardMarkup()
    #btn_key_help = types.InlineKeyboardButton(text='start')
    #markup.add(btn_key_help)
    a = whois(message.chat.username)
    if a[0] == True and a[1] <= 1:
        bot.send_message(message.chat.id, text_help)
    else:
        bot.send_message(message.chat.id, text_no_id)


@bot.message_handler(commands=['count'])
def count_all_user(message):
    a = whois(message.chat.username)
    if a[0] == True and a[1] <= 1:
        a = api_test3.list_count_vpn_user()
        b = str(a)
        bot.send_message(message.chat.id, b)

        #bot.send_message(message.chat.id, text_help)

    else:
        bot.send_message(message.chat.id, text_no_id)
        pass

@bot.message_handler(commands=['count_a'])
def count_active_user(message):
    '''thi function print all count vpn user'''
    au = whois(message.chat.username)
    print(au)
    if au[0] == True and au[1] <= 1:
        a = api_test3.list_count_activity_vpn_user()
        b = str(a)
        bot.send_message(message.chat.id, b)

    else:
        bot.send_message(message.chat.id, text_no_id)
        pass

@bot.message_handler(commands=['list'])
def send_list_vpn_user_name(message):
    ''' this function list all user vpn'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        a = api_test3.list_vpn_user_name()
        b = str(a)
        bot.send_message(message.chat.id, b)
    elif au[0] == False:
        bot.send_message(message.chat.id, text_no_id)
        pass
    else:
        pass

@bot.message_handler(commands=['list_a'])
def send_list_active_vpn_user(message):
    '''this command print list all active user vpn'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        a = api_test3.list_vpn_active_user()
        b = str(a)
        bot.send_message(message.chat.id, b)
    else:
        bot.send_message(message.chat.id, text_no_id)
        pass

#internal get name, experimental
def get_name_u(message, shear):
    '''this function for get name from next command'''
    text = message.text[shear:]
    if len(text) == 0:
        bot.send_message(message.chat.id, 'имя не задано. некого удалять.')
    elif len(text) >= 50:
        bot.send_message(message.chat.id, 'очень много букаф. не могу понять. пожалуйста, короче.')
    else:
        return text

#create new user vpn
@bot.message_handler(commands=['create'])
def create_user(message):
    '''this function create new user vpn, set random name - cocteil
    and generation password. send it in chat'''
    au = whois(message.chat.username)
    #print('я твое имя', au)
    if au[0] == True and au[1] <= 1:
        text = message.text[7:]
        text = text.strip()
        #print('я голый текст')
        if text == None:
            duration = 3600
        elif text.isdigit() == True:
            #print('это же число!')
            if text == 0:
                duration = 3600
            else:
                duration = int(text) * 3600
        elif len(text) == 0:
            duration = 3600
        else:
            #print('не поверишь, но ты тут')
            bot.send_message(message.chat.id, 'это не число. задай число.')
            exit()
        
        a = api_test3.create_vpn_user(duration)
        b = str(a)
        bot.send_message(message.chat.id, b)
    else:
        bot.send_message(message.chat.id, 'что то не то с правами. не буду создавать')
        pass
    
    
    
    #print(text, 'это сырое число')
    

        
    #text = int(text)
    #print(text)


#delete user vpn
@bot.message_handler(commands=['delete'])
def delete_name(message):
    '''this function delete vpn user if exist'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        text = get_name_u(message, 7)
        text = text.strip()
        a = api_test3.remove_vpn_user(text)
        if a == True:
            from api_test3 import close_connection
            close_connection(text)
            bot.send_message(message.chat.id, 'пользователь удален')
        else:
            bot.send_message(message.chat.id, 'увы, такого пользователя нет.')
    else:
        bot.send_message(message.chat.id, text_no_id)
        pass

#def reset active connect from select user vpn

#disable user vpn
@bot.message_handler(commands=['disable'])
def disable_user(message):
    au  = whois(message.chat.username)
    '''this function disable vpn user, if exist'''
    if au[0] == True and au[1] <= 1:
        text = get_name_u(message, 8)
        text = text.strip()
        
        a = api_test3.disable_vpn_user(text)
        if a == True:
            from api_test3 import close_connection
            close_connection(text)
            bot.send_message(message.chat.id, 'пользователь запрещен.')
        else:
            bot.send_message(message.chat.id, 'нет такого пользователя. некого запрещать.')
    else:
        bot.send_message(message.chat.id, text_no_id)
        pass
        
#enable user vpn
@bot.message_handler(commands=['enable'])
def enable_user(message):
    '''this function enable vpn user, if er exist'''
    au  = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        text = get_name_u(message, 7)
        text = text.strip()

        a = api_test3.enable_vpn_user(text)
        if a == True:
            bot.send_message(message.chat.id, 'пользователь разрешен.')
        else:
            bot.send_message(message.chat.id, 'нет такого пользователя. некого разрешать.')

    else:
        bot.send_message(message.chat.id, text_no_id)
        pass

#first auth
#telegram_id = message.chat.id

@bot.message_handler(commands=['auth'])
def auth_admin(message):
    password = message.text[5:]
    if len(password) == 0:
        bot.send_message(message.chat.id, 'не вижу пароля. не пущу.')
    else:
        from create_database import add_admin
        password = password.strip()
        add_admin(password, message.chat.username)
        #print(password,  message.chat.username)
        #print(type(message.chat.username))

@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    '''add new admin from bot'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 0:
        raw_name = message.text[10:]
        raw_name2 = raw_name.strip()
        raw_name3 = re.sub(r'\s+', ' ', raw_name2)
        raw_name4 = raw_name3.split(' ') #if mane str - many elements in corteg
        name_level = raw_name.split(' ')
        name = name_level[1]
        level = name_level[2]
        from create_database import add_admin_mikrotik
        result = add_admin_mikrotik(name, level)
        if result == True:
            text = 'новый администратор успешно создан'
            bot.send_message(message.chat.id, text)
        else:
            text = 'такой админ уже есть.'
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, text_no_id)
        pass
    

@bot.message_handler(commands=['list_connect'])
def list_connect(message):
    '''this function print list all active vpn connection. no arguments'''
    au  = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        a = api_test3.list_active_connections()
        b = str(a)
        if len(a) != 0:
            bot.send_message(message.chat.id,  b)
        else:
            bot.send_message(message.chat.id, 'активных соединений нет.')
    else:
        bot.send_message(message.chat.id, text_no_id)
        pass

@bot.message_handler(commands=['list_admins'])
def list_admins(message):
    '''this function print list all admins bot'''
    from create_database import list_all_admins
    a = list_all_admins()
    b = str(a)
    bot.send_message(message.chat.id, b)
    #add humanize view

@bot.message_handler(commands=['my_time'])
def my_time(message):
    '''this function print left time'''
    from api_test3 import time_left
    text = get_name_u(message, 8)
    text = text.strip()
    
    a = time_left(text)
    print(a)
    #a = a[0]
    if a > 0:
        time_o = a
    else:
        time_o = 'ваше время истекло'
    
    bot.send_message(message.chat.id, time_o)




# Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
bot.remove_webhook()
sleep(5)

# set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
                

# start flask server
app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV), debug=True)
