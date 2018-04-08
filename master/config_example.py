#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  config_example.py

login = 'admin_login'
password = 'admin_password'
host = 'ip or dns from your miktotik'
token = 'token your bot'
bot_admin_password = 'password from first authorization admin-user in bot'

#set environment from web hooks
WEBHOOK_HOST = '138.201.174.71' #set your ip or fqdn
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port open!)
WEBHOOK_LISTEN = '0.0.0.0'  # from any server (not all) == ip up

WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # path to certificat
WEBHOOK_SSL_PRIV = 'webhook_key.pem'  # path to privat key
