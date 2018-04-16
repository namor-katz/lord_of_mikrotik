# -*- coding: utf-8 -*-

from vedis import Vedis
import config


# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id]
        except KeyError:  # Если такого ключа почему-то не оказалось
            return config.States.S_START.value  # значение по умолчанию - начало диалога


# Сохраняем текущее «состояние» пользователя в нашу базу
def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            # тут желательно как-то обработать ситуацию
            return False

#save name
def save_name(name,  value):
    with Vedis(config.db_file) as db:
        try:
            name = db.set(name,  value)
            name.add(value)
            return True
        except:
            return False

#get name
def get_name(user_name):
    with Vedis(config.db_file) as db:
        try:
            return db.get(user_name)
        except KeyError:
            return False

#save time
def save_time(time,  value):
    with Vedis(config.db_file) as db:
        try:
            name = db.set(time,  value)
            name.add(value)
            return True
        except:
            return False

#get time
def get_time(time = 'time'):
    with Vedis(config.db_file) as db:
        try:
            return db.get(time)
        except:
            return False
