#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  generation_name.py
#
#  Copyright 2018 Roman <roman@roman-home>
#test bot from my mikrotik

import telebot
from telebot import types
import logging
import api_test3
from create_database import whois
import re
from time  import sleep
import cherrypy
from os import getpid
import os
import dbworker

#loggin in console
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.


# check cert files if not - create
filename = 'webhook.crt'
if os.access(filename, os.F_OK) == True:
    pass
else:
    from create_cert import create_self_signed_cert
    create_self_signed_cert()

#create pid file
your_pid = getpid()
your_pid = str(your_pid)
pid_file = '/tmp/bot.pid'
with open (pid_file,  'w',  encoding='utf-8') as ff:
    ff.write(your_pid)

import config
WEBHOOK_PORT = config.WEBHOOK_PORT  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = config.WEBHOOK_LISTEN

WEBHOOK_SSL_CERT = config.WEBHOOK_SSL_CERT  # Путь к сертификату
WEBHOOK_SSL_PRIV = config.WEBHOOK_SSL_PRIV  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (config.WEBHOOK_HOST, config.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

# event handling from keyboard
text_help = '/count - количество юзеров, всего; \n /count_a - активных юзеров; \n \
/list - показать имена всех; \n /list_a - показать имена активных; \n /create - создать нового юзера \n \
/delete - удалить юзера \n /disable - запретить юзера; \n /enable - разрешить юзера \n /add_admin - добавить нового администратора \n \
/list_connect - кто подключен сейчас? \n /list_admins - список админов \n /my_time - сколько осталось времени? \n '

text_no_id = 'такого адмнинистратора нет. Попросите вас добавить.'
#create castom keyboard
markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
itembtn1 = types.KeyboardButton('администраторы')
itembtn2 = types.KeyboardButton('пользователи')
markup.add(itembtn1, itembtn2)
#bot.send_message(m.chat.id, "нажми любую кнопку", reply_markup=markup)

#create subkeyboard users
markup2 = types.ReplyKeyboardMarkup(row_width=3,  resize_keyboard=True) #submenu users
itembtn1 = types.KeyboardButton('создать')
itembtn2 = types.KeyboardButton('удалить')
itembtn3 = types.KeyboardButton('запретить')
itembtn4 = types.KeyboardButton('разрешить')
itembtn5 = types.KeyboardButton('подключенные')
itembtn6 = types.KeyboardButton('всего')
markup2.add(itembtn1, itembtn2,  itembtn3,  itembtn4,  itembtn5,  itembtn6)

#create subkeyboard admins
markup3 = types.ReplyKeyboardMarkup(row_width=3,  resize_keyboard=True) #submenu admins
itembtn1 = types.KeyboardButton('добавить')
itembtn2 = types.KeyboardButton('список')
itembtn3 = types.KeyboardButton('главное_меню')
markup3.add(itembtn1, itembtn2)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,  'нажми любую кнопку',  reply_markup=markup)

@bot.message_handler(regexp='администраторы')
def administrators(message):
    bot.send_message(message.chat.id,  'вы в меню администраторы',  reply_markup=markup3)

@bot.message_handler(regexp='пользователи')   
def users(message):
    bot.send_message(message.chat.id,  'вы в меню пользователи',  reply_markup=markup2)

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


@bot.message_handler(regexp='всего')
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
text_get_name = 'укажите имя нового пользователя, либо нажмите "отправить" чтобы имя создалось автоматически'
text_get_time = 'укажите время, цифрами, в часах.'
text_final = 'пробую создать пользователя...'

@bot.message_handler(commands=['create'])
def create_user(message):
    '''this function create new user vpn, set random name - cocteil
    and generation password. send it in chat'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        #state = dbworker.get_current_state(message.chat.id)
        bot.send_message(message.chat.id,  text_get_name)
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)
        #state = dbworker.get_current_state(message.chat.id)
        #if state == config.States.S_START.value:
            
            #dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)
            #name = get_name(message)
            #if len(name) == 0:
                #from generation_name2 import create_name
                #name = create_name()
        #else:
            #pass
        ''''
        state = dbworker.get_current_state(message.chat.id)
        if state == config.States.S_TIME.value:
            bot.send_message(message.chat.id,  text_get_time)
            time_user = get_time(message)
        else:
            pass
           
        a = api_test3.create_vpn_user(zero_name,  duration)
        b = a['name']
        b = str(b)
        c = a['password']
        c = str(c)
        d = 'логин ' + b + ' пароль ' + c
        bot.send_message(message.chat.id, d)
        '''
    else:
        bot.send_message(message.chat.id, 'что то не то с правами. не буду создавать')
        pass

@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "clear")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def get_name(message):
    '''get name if exist, set next step - get time'''
    bot.send_message(message.chat.id,  text_get_time)
    name = message.text
    name = name.strip()
    name2 = name + ' - это имя'
    bot.send_message(message.chat.id,  name2)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_TIME.value)
    print('я есть имя: ',  name)
    if name.isdigit():
        str(name)
    #dbworker.save_name(message.chat.id,  name)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_TIME.value)
def get_time(message):
     '''get time from user to poweroff'''
     bot.send_message(message.chat.id,  text_final)
     time_user = message.text[0:]
     time_user = time_user.strip()
     time_user = str(time_user)
     #print('я есть время: ',  time_user)
     dbworker.save_time(message.chat.id,  time_user)
     dbworker.set_state(message.chat.id, config.States.S_ENTER_FINAL.value)
     
     return True #was shreiben?

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_FINAL.value)
def final_create(message):
    pass
    

#delete user vpn
@bot.message_handler(commands=['delete'])
def delete_name(message):
    '''this function delete vpn user if exist'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        text = get_name_u(message, 7)
        #print('в смысле нот тайп',  text)
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
    '''this function adds the first administrator'''
    password = message.text[5:]
    if len(password) == 0:
        bot.send_message(message.chat.id, 'не вижу пароля. не пущу.')
    else:
        from create_database import add_admin
        password = password.strip()
        a = add_admin(password, message.chat.username)
        if a == True:
            bot.send_message(message.chat.id,  'администратор добавлен')
        else:
            bot.send_message(message.chat.id,  'увы, я никого не добавил')
        #print(password,  message.chat.username)
        #print(type(message.chat.username))

@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    '''this function add new admin from bot'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 0:
        raw_name = message.text[10:]
        raw_name2 = raw_name.strip()
        raw_name3 = re.sub(r'\s+', ' ', raw_name2)
        #raw_name4 = raw_name3.split(' ') #if mane str - many elements in corteg
        name_level = raw_name3.split(' ')
        #print(len(name_level))
        if len(name_level) == 2:
            name = name_level[0]
            level = name_level[1]
        else:
            bot.send_message(message.chat.id,  'нужно указать телеграм-нейм нового админа и его левел')
            exit()
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
    text = get_name_u(message, 8) #тут влетает 'имя не указано, удалять нечего' из get_name_u
    #print('я текст из май тайм',  text)
    if text == None:
        bot.send_message(message.chat.id,  'не указано имя, показывать нечего')
        exit()
    else:
        text = text.strip()

    a = time_left(text)
    print(a)
    #a = a[0]
    if a > 0:
        time_o = a / 60
        time_o = int(time_o)
        time_o = str(time_o) + ' минут осталось'
    else:
        time_o = 'ваше время истекло'

    bot.send_message(message.chat.id, time_o)

# Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
bot.remove_webhook()
sleep(3)

# set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

# start cherrypy server
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
