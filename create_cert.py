#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create_cert.py
#
#  Copyright 2018 Roman <rk@staffcop.ru>

from OpenSSL import crypto, SSL
from socket import gethostname
from pprint import pprint
from time import gmtime, mktime
from os.path import exists, join
from datetime import datetime, timedelta
import requests

internal_ip = requests.get('http://ipinfo.io').json()
internal_ip2 = internal_ip.get('ip')

CN = 'webhook'
CERT_FILE = "%s.crt" % CN
KEY_FILE = "%s.key" % CN
#now    = datetime.now()
#expire = now + timedelta(days=365)


def create_self_signed_cert(cert_dir="."):
    C_F = join(cert_dir, CERT_FILE)
    K_F = join(cert_dir, KEY_FILE)
    if not exists(C_F) or not exists(K_F):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)
        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "RU"
        cert.get_subject().ST = "Russland"
        cert.get_subject().L = "Nsk"
        cert.get_subject().O = "Home"
        cert.get_subject().OU = "Sofa"
        cert.get_subject().CN = internal_ip2
        cert.get_subject().emailAddress = 'namor925@gmail.com'
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(315360000)
        #cert.set_notBefore(now.strftime("%Y%m%d%H%M%SZ").encode())
        #cert.set_notAfter(expire.strftime("%Y%m%d%H%M%SZ").encode())
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')
        with open(C_F, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            '''
            a = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            b = a.encode('utf-8')
            print(a)
            print(type(a))
            '''
        with open(K_F, "wb") as ff:
            ff.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        print('generation success!')
    else:
        print('keys exists!')

create_self_signed_cert()
