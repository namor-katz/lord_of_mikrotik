#!/usr/bin/env python
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

#create castom keyboard from admin level0
markup0 = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
itembtn1 = types.KeyboardButton('администраторы')
itembtn2 = types.KeyboardButton('пользователи')
itembtn3 = types.KeyboardButton('информация')
markup0.add(itembtn1, itembtn2,  itembtn3)

#create custom keyboard from admin level1
markup1 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#itembtn1 = types.KeyboardButton('администратор')
itembtn2 = types.KeyboardButton('пользователи')
itembtn3 = types.KeyboardButton('информация')
markup1.add(itembtn2,  itembtn3)

#create custom keyboard from admin level2
markup2 = types.ReplyKeyboardMarkup(row_width=2,  resize_keyboard = True)
itembtn1 = types.KeyboardButton('информация')
markup2.add(itembtn1)

#create subkeyboard admins
admins_keyboard = types.ReplyKeyboardMarkup(row_width=3,  resize_keyboard = True)
itembtn1 = types.KeyboardButton('добавить')
itembtn2 = types.KeyboardButton('удалить')
itembtn3 = types.KeyboardButton('список')
itembtn4 = types.KeyboardButton('главное_меню')
admins_keyboard.add(itembtn1,  itembtn2,  itembtn3, itembtn4)

#create subkeyboard users
users_keyboard = types.ReplyKeyboardMarkup(row_width = 3,  resize_keyboard = True)
itembtn1 = types.KeyboardButton('создать')
itembtn2 = types.KeyboardButton('удалить')
itembtn3 = types.KeyboardButton('запретить')
itembtn4 = types.KeyboardButton('разрешить')
itembtn5 = types.KeyboardButton('подключенные')
itembtn6 = types.KeyboardButton('всего')
itembtn7 = types.KeyboardButton('перечень')
itembtn8 = types.KeyboardButton('информация')
itembtn9 = types.KeyboardButton('продлить')
itembtn10 = types.KeyboardButton('главное_меню')
users_keyboard.add(itembtn1, itembtn2,  itembtn3,  itembtn4,  itembtn5,  itembtn6,  itembtn7,  itembtn8,  itembtn9, itembtn10)


@bot.message_handler(commands=['start'])
def start(message):
    '''This function displays various menus depending on the administrator's level'''
    au = whois(message.chat.username)
    print(au)
    if au[0] == True and au[1] == 0:
        bot.send_message(message.chat.id,  'нажми любую кнопку',  reply_markup=markup0)
    elif au[0] == True and au[1] == 1:
        bot.send_message(message.chat.id,  'нажми любую кнопку',  reply_markup=markup1)
    elif au[0] == True and au[1] == 2:
        bot.send_message(message.chat.id,  'нажми любую кнопку',  reply_markup=markup2)
    else:
        bot.send_message(message.chat.id,  'нажми любую кнопку',  reply_markup=markup2)


@bot.message_handler(regexp='главное_меню')
def back(message):
    start(message)
    
@bot.message_handler(regexp='администраторы')
def administrators(message):
    bot.send_message(message.chat.id,  'вы в меню администраторы',  reply_markup=admins_keyboard)

@bot.message_handler(regexp='пользователи')   
def users(message):
    bot.send_message(message.chat.id,  'вы в меню пользователи',  reply_markup=users_keyboard)

@bot.message_handler(commands=['help'])
def help_for_bot(message):
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

@bot.message_handler(regexp = 'перечень')
def send_list_vpn_user_name(message):
    ''' this function list all user vpn'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        a = api_test3.list_vpn_user_name()
        #print(type(a))
        #b = str(a)
        bot.send_message(message.chat.id, 'существуют следующие пользователи')
        temp_user_str = ''
        for i in a:
            temp_user_str = i + ',  ' + temp_user_str
        bot.send_message(message.chat.id, temp_user_str)
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

@bot.message_handler(regexp='создать')
def create_user(message):
    '''this function create new user vpn, set random name - cocteil
    and generation password. send it in chat'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        #dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)
        state = dbworker.get_current_state(message.chat.id)
        if state == config.States.S_START.value:
            bot.send_message(message.chat.id,  text_get_name)
            dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)
        elif state == config.States.S_ENTER_NAME.value:
            bot.send_message(message.chat.id,  'введите имя')
        elif state == config.States.S_ENTER_TIME.value:
            bot.send_message(message.chat.id,  'введите время')
        elif state == config.States.S_ENTER_FINAL.value:
            final_create(message)
        else:
            bot.send_message(message.chat.id,  text_get_name)
            dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)
        
    else:
        bot.send_message(message.chat.id, 'что то не то с правами. не буду создавать')
        pass

@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "clear")
    dbworker.set_state(message.chat.id, config.States.S_START.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value) #1!
def get_name(message):
    '''get name if exist, set next step - get time'''
    name = message.text.strip()
    #sleep(1)
    #name = name.strip()
    dbworker.set_state(message.chat.id, config.States.S_ENTER_TIME.value) #set 2
    print('set2!')
    dbworker.save_name('name',  name)
    print('я есть имя: ',  name)
    #dbworker.save_name(message.chat.id,  name)
    bot.send_message(message.chat.id,  text_get_time)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_TIME.value)#2!
def get_time(message):
     '''get time from user to poweroff'''
     #bot.send_message(message.chat.id,  text_get_time)
     time_user = message.text.strip()
     #time_user = time_user.strip()
     #time_user = str(time_user)
     dbworker.save_time('time',  time_user)
     print('я есть время: ',  time_user)
     #dbworker.save_time(message.chat.id,  time_user)
     print('ща поставлю финал!')
     dbworker.set_state(message.chat.id, config.States.S_ENTER_FINAL.value)
     print('поставил финал')
     print(message.chat.id)
     bot.send_message(message.chat.id, 'отправьте любой символ для подтверждения создания.')
  
     

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_FINAL.value)#3
def final_create(message):
    bot.send_message(message.chat.id,  text_final)
    name = dbworker.get_name('name')
    print('получил наме из базы')
    time_to_off = dbworker.get_time()
    print('получил тайм из базы')
    if time_to_off == False:
        print("не, не получил")
    print('я имя!',  name)
    print('я время',  time_to_off)
    a = api_test3.create_vpn_user(name,  int(time_to_off))
    b = a['name']
    b = str(b)
    c = a['password']
    c = str(c)
    d = 'логин ' + b  + ' пароль ' + c
    bot.send_message(message.chat.id,  d)
    dbworker.set_state(message.chat.id, config.States.S_START.value)

#delete user vpn
@bot.message_handler(regexp = 'удалить')
def delete_name(message):
    '''просим имя'''
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        state = dbworker.get_current_state(message.chat.id)
        if state == config.States.S_START.value:
            bot.send_message(message.chat.id,  'введите имя удаляемого пользователя')
            dbworker.set_state(message.chat.id,  config.States.delete_del.value)
        elif state == config.States.delete_del.value:
            bot.send_message(message.chat.id,  'у вас есть неудаленный пользователь. продолжите \
            удаление или выполните команду /reset для отмены.')
        else:
            dbworker.set_state(message.chat.id,  config.States.S_START.value)
            bot.send_message(message.chat.id,  'что то пошло не так, я вернулся к исходному состоянию.\
            начните всё с начала.')
    else:
        bot.send_message(message.chat.id, text_no_id)
        pass
        
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.delete_del.value)
def delete_name2(message):
    """берем имя и удаляем"""
    name = message.text.strip()
    from create_database import user_exist
    a = user_exist(name)
    if a == False:
        bot.send_message(message.chat.id, 'увы, такого пользователя нет. проверьте имя на опечатки, и повторите ввод.')
    elif a == True:
        from api_test3 import remove_vpn_user
        dbworker.set_state(message.chat.id,  config.States.S_START.value)
        a = remove_vpn_user(name)

        from api_test3 import close_connection
        close_connection(name)
        from create_database import delete_user_from_database
        delete_user_from_database(name)
        bot.send_message(message.chat.id, 'пользователь удален')


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
@bot.message_handler(regexp = 'разрешить')
def enable_user(message):
    """берет имя, которое надо разрешить"""
    au = whois(message.chat.username)
    if au[0] == True and au[1] <= 1:
        state = dbworker.get_current_state(message.chat.id)
        if state == config.States.S_START.value:
            bot.send_message(message.chat.id,  'введите имя разрешаемого пользователя')
            dbworker.set_state(message.chat.id,  config.States.enable_get.value)
        elif state == config.States.enable_get.value:
            bot.send_message(message.chat.id,  'вы начали разрешать пользователя, но не завершили\
            завершите разрешение, или сбросьте все командой /reset')
        else:
            bot.send_message(message.chat.id,  'что то пошло не так, я сбросил все к началу.')
            dbworker.set_state(message.chat.id,  config.States.S_START.value)
    else:
        bot.send_message(message.chat.id, text_no_id)
            
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.enable_get.value)
def enable_user2(message):
    """разрешает это имя."""
    name = message.text.strip()
    print(name)
    from create_database import user_exist
    a = user_exist(name)
    print(a)
    if a == False:
        bot.send_message(message.chat.id, 'увы, такого пользователя нет. проверьте имя на опечатки, и повторите ввод.')
    elif a == True:
        from api_test3 import enable_vpn_user
        b = enable_vpn_user(name)
        if b == True:
            bot.send_message(message.chat.id,  'пользователь разрешен')
        else:
            bot.send_message(message.chat.id,  'на роутере нет такого пользователя. обратитесь к администратору')

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

@bot.message_handler(regexp = 'добавить')
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


@bot.message_handler(regexp = 'подключенные')
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

@bot.message_handler(regexp='список')
def list_admins(message):
    '''this function print list all admins bot'''
    from create_database import list_all_admins
    a = list_all_admins()
    bot.send_message(message.chat.id, 'есть следующие администраторы:')
    for i in a:
        t1 = i[0]
        t2 = i[1]
        t3 = 'админ ' + t1 + ' с уровнем доступа ' + str(t2)
        bot.send_message(message.chat.id, t3)


#add extra time
@bot.message_handler(regexp = 'продлить')
def add_extra_time(message):
    """запрашивает первый аргумент"""
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_START.value:
        bot.send_message(message.chat.id, 'введите имя пользователя, которому требуется \
        дать дополнительное время.')
        dbworker.set_state(message.chat.id, config.States.add_time_name.value)
    elif state == config.States.add_time_name.value:
        bot.send_message(message.chat.id,  'у вас есть пользователь с непродленным \
        временем. введите его имя, либо выполните /reset')
    elif state == config.States.add_time_time.value:
        bot.send_message(message.chat.id,  'у вас есть пользователь, имя которого введено, но время не продлено.\
        укажите время в часах, цифрами')
    else:
        pass
        
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.add_time_name.value)
def add_extra_time2(message):
    """берет имя, запрашивает время"""
    name = message.text.strip()
    from create_database import user_exist
    a = user_exist(name)
    dbworker.save_name('name_from_add_time', name)
    if a == False:
        bot.send_message(message.chat.id, 'увы, такого пользователя нет. проверьте имя на опечатки, и повторите ввод.')
    elif a == True:
        bot.send_message(message.chat.id,  'введите время, на которое нужно продлить сеанс пользователя.\
        указывайте время цифрами, в часах.')
        dbworker.set_state(message.chat.id,  config.States.add_time_time.value)        
    else:
        bot.send_message(message.chat.id,  'вы не должны были здесь оказаться. обратитесь к администратору.')
 
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.add_time_time.value) 
def add_extra_time3(message):
    """'это берет время, на которое надо продлить, и продляет."""
    duration = message.text.strip()
    if duration.isdigit() == True:
        bot.send_message(message.chat.id,  'ок, добавляю время.') #!!проверять на -!!
        dbworker.set_state(message.chat.id,  config.States.S_START.value)
        #взять имя из бд
        from create_database import add_time2
        username = dbworker.get_name('name_from_add_time')
        a = add_time2(username,  duration)
        if a == True:
            bot.send_message(message.chat.id,  'время добавлено успешно')
        elif a == False:
            bot.send_message(message.chat.id,  'что то пошло не так, не добавлено')
        else:
            bot.send_message(message.chat.id,  'что то пошло не так. обратитесь к администратору.')
        #если тру - ок, продлено
    else:
        bot.send_message(message.chat.id,  'увы, это не число. Введите, пожалуйста, число.')
        
#return info (left_time) from user
@bot.message_handler(regexp = 'информация')
def my_time(message):
    '''this function print left time'''
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_START.value:
        bot.send_message(message.chat.id,  'введите имя пользователя, информацию о котором нужно получить.')
        dbworker.set_state(message.chat.id, config.States.USER_INFO_GET.value)
    elif state == config.States.USER_INFO_GET.value:
        bot.send_message(message.chat.id, 'введите имя.')
    else:
        bot.send_message(message.chat.id,  'введите имя пользователя, информацию о котором нужно получить.')
        dbworker.set_state(message.chat.id, config.States.USER_INFO_GET.value)
   

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.USER_INFO_GET.value)
def send_info(message):
    '''send info to chat'''
    from api_test3 import time_left
    a = time_left(message.text)
    #print(type(a))
    if a < 0:
        bot.send_message(message.chat.id,  'ваше время истекло.')
        dbworker.set_state(message.chat.id,  config.States.S_START.value)
    elif a > 0:
        c = a / 60
        c = int(c)
        c = str(c)
        b = 'осталось ' + c + ' минут(ы)' #??
        bot.send_message(message.chat.id, b)
        dbworker.set_state(message.chat.id,  config.States.S_START.value)
    elif a == False:
        bot.send_message(message.chat.id,  'увы, такого пользователя нет. Проверьте имя на опечатки, и введите еще раз.')
    else:
        bot.send_message(message.chat.id,  'вы не должны были здесь оказаться. \
        что то пошло не так. сообщите об этом администратору.')



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
