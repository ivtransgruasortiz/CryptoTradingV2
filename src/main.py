import ast
import logging
import math
import os
import ssl
import sys
import time
import datetime

import math
import requests as rq
import yaml
import pandas as pd
import tqdm
import numpy as np

from coinbase import jwt_generator
from coinbase.rest import RESTClient

import utils.constants as cons
from utils.functions import Headers, get_accounts, get_accounts_sdk, disposiciones_iniciales, \
    historic_df_sdk, toma_1, fechas_time, df_medias_bids_asks, pintar_grafica

if __name__ == "__main__":
    logging \
        .basicConfig(format='%(asctime)s %(name)s-%(levelname)s:: %(message)s',
                     datefmt='%Y-%m-%d %H:%M:%S',
                     level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    crypto_log = logging.getLogger("Crypto_Logging")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 20)

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

    ###########################
    # START REAL-TIME TRADING #
    ###########################
    crypto_log.info('### Data OK! ###')
    print('\n### Real-Time Processing... ### - \nPress CTRL+C (QUICKLY 2-TIMES!!) to cancel and view results')

    # PARAMETROS INICIALES
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

    # #########################
    # # #### CONSULTAS #######
    # #########################
    # # FORMA 0 - CON SDK (Software Development Kit)
    # client = RESTClient(api_key=api_key, api_secret=api_secret)
    # jwt_token = jwt_generator.build_ws_jwt(api_key, api_secret) # no hace falta pero como lo pongo como info
    # accounts = client.get_accounts()[cons.ACCOUNTS]
    # accounts_crypto = [x["available_balance"] for x in accounts if x["available_balance"]["value"] != "0"]
    # disp_ini = disposiciones_iniciales(client)
    # # FORMA 1 - CON CLASS ResApi
    # endpoint = "/api/v3/brokerage/best_bid_ask"
    # restapi = RestApi(api_key, api_secret, cons.GET, endpoint)
    # jsonresp = restapi.rest()
    # # FORMA 2 - CON REQUESTS
    # endpoint = f"/api/v3/brokerage/products/{crypto}/ticker"
    # extras = "limit=500"
    # endpoint_path = cons.HTTPS + cons.REQUEST_HOST + endpoint + extras
    # header_ks = Headers(api_key, api_secret)
    # endpoint_path = cons.HTTPS + cons.REQUEST_HOST + "?".join([endpoint, header_ks.extras()])
    # res = rq.get(endpoint_path, headers=header_ks.headers(cons.GET, endpoint))
    # res.json()

    # OBTENEMOS LAS DISPOSICIONES INICIALES DE LA CUENTA
    disp_ini = get_accounts(api_key, api_secret)
    disp_ini_sdk = get_accounts_sdk(api_key, api_secret)
    eur = math.trunc(disp_ini_sdk[cons.EUR] * 100) / 100
    crypto_quantity = math.trunc(disp_ini_sdk[crypto_short] * 100) / 100

    # Historico mejorado para el script
    hist_df = historic_df_sdk(api_key, api_secret, crypto=cons.BTC_EUR, t_hours_back=3, limit=1000)

    df_tot = hist_df
    # df_tot['bids_1'] = np.vectorize(toma_1)(df_tot['bids'])
    # df_tot['asks_1'] = np.vectorize(toma_1)(df_tot['asks'])
    df_tot['time_1'] = np.vectorize(fechas_time)(df_tot['time'])
    df_tot = df_tot.sort_values('time_1', ascending=True)
    df_tot = df_tot[['time_1', 'price']].drop_duplicates().reset_index()

    # todo be continue... cambiar crypto a btc... comprobar len dataframes

    ordenes = hist_df[['bids', 'asks', 'sequence']].to_dict(orient='records')
    bids = [x[0][0] for x in list(hist_df['bids'].values)]
    asks = [x[0][0] for x in list(hist_df['asks'].values)]

    # MEDIAS EXP HISTORICAS
    fechas = [x for x in df_tot['time_1']]

    # ### PINTAR GRAFICAS ###
    grafica = True
    len(fechas)
    len(asks)
    len(df_tot)
    len(ordenes)
    if grafica:
        df_hist_exp = df_medias_bids_asks(asks, crypto, fechas, n_rapida_asks, n_lenta_asks)
        pintar_grafica(df_hist_exp, crypto)
    else:
        pass


