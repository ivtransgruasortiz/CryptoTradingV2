import ast
import logging
import math
import os
import ssl
import sys
import time

import yaml

from coinbase.rest import RESTClient
import hmac, hashlib, base64
import requests as rq
from requests.auth import AuthBase
import http.client
import json

import jwt
from coinbase import jwt_generator
from cryptography.hazmat.primitives import serialization
import time
import secrets

import utils.constants as cons
from utils.functions import disposiciones_iniciales, historic_df, build_jwt

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

    api_key = str(os.environ.get('API_KEY'))
    api_secret = str(os.environ.get('API_SECRET')) \
        .replace("\\n", "\n")

    # # Parametros iniciales
    crypto = param['crypto']
    crypto_short = crypto.split('-')[0]
    trigger_tramos = param['trigger_tramos']
    n_tramos = param['n_tramos']
    inversion_fija_eur = param['inversion_fija_eur']
    api_url = param['api_url']
    t_limit_percentile = param['t_limit_percentile']
    pmax = param['pmax']
    pmin = param['pmin']
    margenmax = param['margenmax']
    margentramo = param['margentramo']
    time_percen_dicc = param['time_percen_dicc']
    pag_historic = param['pag_historic']
    freq_exec = param['freq_exec']
    contador_ciclos = param['contador_ciclos']
    tamanio_listas_min = freq_exec * time_percen_dicc['tiempo_caida_1']
    factor_tamanio = param['factor_tamanio']
    ordenes_lanzadas = []
    n_rapida_bids = param['n_rapida_bids']
    n_lenta_bids = param['n_lenta_bids']
    n_rapida_asks = param['n_rapida_asks']
    n_lenta_asks = param['n_lenta_asks']
    n_media = param['n_media']
    grafica = param['grafica']
    nummax = param['nummax']
    redefinicion_max = param['redefinicion_max']

    #########################
    # #### CONSULTAS #######
    #########################

    # # FORMA 1 - CON SDK (Software Development Kit)
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    accounts = client.get_accounts()[cons.ACCOUNTS]
    accounts_crypto = [x["available_balance"] for x in accounts if x["available_balance"]["value"] != "0"]
    # Disp_iniciales - OPCIONAL SOLO POR INFORMACION
    disp_ini = disposiciones_iniciales(client)

    # # FORMA 2 - CON API-REST
    request_method = "GET"
    request_host = "api.coinbase.com"
    request_path = "/api/v3/brokerage/accounts"
    request_path = "/api/v3/brokerage/best_bid_ask"

    uri = f"{request_method} {request_host}{request_path}"
    jwt_token = build_jwt(api_key, api_secret, uri)
    # CON SDK (no funciona bien)
    jwt_token = jwt_generator.build_ws_jwt(api_key, api_secret)

    conn = http.client.HTTPSConnection(request_host)
    payload = ''
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {jwt_token}"
    }
    # con conn
    conn.request("GET", request_path, payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    # con requests
    res = rq.get("https://"+request_host+request_path, headers=headers)
    res.json()

    # TODO - CONTINUAR DESDE AQUI, IMPLEMENTAR UNA FUNCIÓN PARA HACER LAS PETICIONES REST Y POST ADECUADAS
    # TODO - CONTINUAR VER QUE PASA CON LAS CUENTAS QUE NO SALEN TODAS LAS CRYPTO NI LOS EUR

    hist_df = historic_df(param['crypto'], param['api_url'], auth, param['pag_historic'])

    crypto_quantity = math.trunc(disp_ini[crypto_short] * 100) / 100
    eur = math.trunc(disp_ini['EUR'] * 100) / 100

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
