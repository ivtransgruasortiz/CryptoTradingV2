import ast
import sys
import os

import time
import requests as rq
import math
import datetime
import dateutil.parser
from dateutil import tz
from dateutil.tz import *
import yaml
import pandas as pd
import numpy as np

import json
import smtplib
import ssl
import matplotlib.pyplot as plt
from string import ascii_lowercase
import random

from statistics import mean
from scipy import stats

from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client as client_whatsapp_twilio
import tweepy

import logging

import http.client

import utils.constants as cons
from utils.functions import ema, tiempo_pausa_new, CoinbaseExchangeAuth, buy_sell, condiciones_buy_sell, \
    medias_exp, df_medias_bids_asks, pintar_grafica, limite_tamanio, limite_tamanio_df, historic_df, \
    disposiciones_iniciales, stoploss, automated_mail, automated_whatsapp, toma_1, fechas_time, \
    porcentaje_variacion_inst_tiempo, percentil, tramo_inv, trigger_list_last_buy, random_name, bool_compras_previas


if __name__ == "__main__":
    logging \
        .basicConfig(format='%(asctime)s %(name)s-%(levelname)s:: %(message)s',
                     datefmt='%Y-%m-%d %H:%M:%S',
                     level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    crypto_log = logging.getLogger("Crypto_Logging")

    # Importar Parametros
    with open('utils/parameters.yaml', 'r') as parameters_file:
        param = yaml.safe_load(parameters_file)
        parameters_file.close()

    try:
        local_execution = ast.literal_eval(os.environ.get(cons.LOCAL_EXECUTION))
    except Exception as e1:
        local_execution = False
        logging.info(f"INFO: local_execution = False - {e1}")
        print(f"INFO: local_execution = False - {e1}")

    if local_execution:
        logging.info(f"INFO!! - Executing in local mode")
        print(f"INFO!! - Executing in local mode")
        # list_months = os.getenv(cons.LISTMONTHS)
        # kind_cross = os.getenv(cons.KIND_CROSS)

    else:
        logging.info(f"INFO!! - Executing in host mode")
        print(f"INFO!! - Executing in host mode")
        # list_months = sys.argv[1]
        # kind_cross = sys.argv[2]

    print(
        f"""\nRunning with arguments:
            - local_execution: {local_execution}"""
    )

    API_KEY = str(os.environ.get('API_KEY'))
    PASSPHRASE = str(os.environ.get('PASSPHRASE'))
    SECRET_KEY = str(os.environ.get('SECRET_KEY'))










    ####
    if '__file__' in locals():
        auth = CoinbaseExchangeAuth(sys.argv[1], sys.argv[2], sys.argv[3])
        client_r = pymongo.MongoClient(
            "mongodb+srv://%s:%s@cluster0.vsp3s.mongodb.net/" % (sys.argv[4], sys.argv[5]), ssl_cert_reqs=ssl.CERT_NONE)
        db_twilio = client_r.get_database(whatsapp_twilio_db)
        db_mail = client_r.get_database(mail_db)
        db_twitter = client_r.get_database(twitter_db)
        client = pymongo.MongoClient(
            "mongodb+srv://%s:%s@cluster0.vsp3s.mongodb.net/%s?retryWrites=true&w=majority" % (sys.argv[4],
                                                                                               sys.argv[5],
                                                                                               crypto_trading_db),
            ssl_cert_reqs=ssl.CERT_NONE)
        db = client.get_database(crypto_trading_db)
    else:
        with open('config.yaml', 'r') as config_file:
            cred = yaml.safe_load(config_file)
            config_file.close()
        auth = CoinbaseExchangeAuth(cred['Credentials'][0], cred['Credentials'][1], cred['Credentials'][2])
