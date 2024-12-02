import ast
import hashlib
import logging
import math
import os
import ssl
import sys
import time
from dateutil import tz
from dateutil.tz import *
import datetime

import math
import requests as rq
import yaml
import pandas as pd
import tqdm
import numpy as np

from coinbase import jwt_generator
from coinbase.rest import RESTClient

from cryptography.fernet import Fernet

from tinydb import TinyDB, where

import matplotlib as mpl
import matplotlib.pyplot as plt

import utils.parameters as param
import utils.constants as cons
import utils.creds as cred
from utils.functions import Headers, get_accounts, get_accounts_sdk, disposiciones_iniciales, \
    historic_df_sdk, toma_1, fechas_time, df_medias_bids_asks, pintar_grafica, medias_exp, sma, tramo_inv, \
    encrypt, decrypt, fechas_time_utc, ema, limite_tamanio, limite_tamanio_df

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

    try:
        local_execution = ast.literal_eval(os.environ.get(cons.LOCAL_EXECUTION))
    except Exception as e1:
        local_execution = False
        logging.info(f"INFO: local_execution = False - {e1}")
        print(f"INFO: local_execution = False - {e1}")

    if local_execution:
        logging.info(f"INFO!! - Executing in local mode")
        print(f"INFO!! - Executing in local mode")
        passphrase = os.getenv(cons.PASSPHRASE)
    else:
        logging.info(f"INFO!! - Executing in host mode")
        print(f"INFO!! - Executing in host mode")
        passphrase = sys.argv[1]

    print(
        f"""\nRunning with arguments:
            - local_execution: {local_execution}"""
    )

    # # PARA CODIFICAR
    # api_key = str(os.environ.get(cons.API_KEY))
    # api_secret = str(os.environ.get(cons.API_SECRET)) \
    #     .replace("\\n", "\n")
    # passphrase = Fernet.generate_key()
    # token_api_key = encrypt(api_key.encode(), passphrase.encode())
    # token_api_secret = encrypt(api_secret.encode(), passphrase.encode())

    # PARA DESCODIFICAR
    token_api_key = cred.token_api_key
    token_api_secret = cred.token_api_secret
    api_key = decrypt(token_api_key, passphrase.encode()).decode().replace("\\n", "\n")
    api_secret = decrypt(token_api_secret, passphrase.encode()).decode().replace("\\n", "\n")

    ###########################
    # START REAL-TIME TRADING #
    ###########################
    crypto_log.info('### Data OK! ###')
    print('\n### Real-Time Processing... ### - \nPress CTRL+C (QUICKLY 2-TIMES!!) to cancel and view results')

    # PARAMETROS INICIALES
    crypto_short = param.CRYPTO.split('-')[0]
    tamanio_listas_min = param.FREQ_EXEC * param.TIME_PERCEN_DICC['tiempo_caida_1']
    ordenes_lanzadas = []

    # OBTENEMOS LAS DISPOSICIONES INICIALES DE LA CUENTA
    # disp_ini = get_accounts(api_key, api_secret)
    disp_ini_sdk = get_accounts_sdk(api_key, api_secret)
    eur = math.trunc(disp_ini_sdk[cons.EUR] * 100) / 100
    crypto_quantity = math.trunc(disp_ini_sdk[crypto_short] * 100) / 100

    # FEES - TASAS COINBASE SEGUN MOVIMIENTOS
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    fees = client.get_transaction_summary()[cons.FEE_TIER]
    fees_pricing_tier = fees[cons.PRICING_TIER]
    fees_taker = round(float('%.4f' % (float(fees[cons.TAKER_FEE_RATE]))), 4)
    fees_maker = round(float('%.4f' % (float(fees[cons.MAKER_FEE_RATE]))), 4)

    # HISTORICO MEJORADO PARA EL SCRIPT
    hist_df = historic_df_sdk(api_key, api_secret, crypto=cons.BTC_EUR, t_hours_back=param.T_HOURS_BACK, limit=1000)
    hist_df[cons.BIDS] = [[[x, y]] for x, y in
                       zip(hist_df[cons.PRICE], hist_df[cons.SIZE])]
    hist_df[cons.ASKS] = [[[x, y]] for x, y in
                       zip(hist_df[cons.PRICE], hist_df[cons.SIZE])]
    bids = [x[0][0] for x in list(hist_df[cons.BIDS].values)]
    asks = [x[0][0] for x in list(hist_df[cons.ASKS].values)]
    ordenes = hist_df[[cons.BIDS, cons.ASKS, cons.TIME]].to_dict(orient=cons.RECORDS)

    # HISTORICO MEJORADO PARA EL SCRIPT
    df_tot = hist_df.loc[:]
    df_tot[cons.BIDS_1] = np.vectorize(toma_1)(df_tot[cons.BIDS])
    df_tot[cons.ASKS_1] = np.vectorize(toma_1)(df_tot[cons.ASKS])
    df_tot[cons.TIME_1] = np.vectorize(fechas_time_utc)(df_tot[cons.TIME])
    df_tot = df_tot.sort_values(cons.TIME_1, ascending=True).reset_index()
    df_tot = df_tot[[cons.TIME_1, cons.BIDS_1, cons.ASKS_1]]

    # MAXIMO NUMERO DE DECIMALES
    n_decim = max([len(str(x[0][0]).split('.')[1]) for x in list(hist_df[cons.ASKS].values)])
    list_sizes = [x for x in list(hist_df[cons.SIZE].values) if "." in str(x)]
    n_decim_size = max([len(str(float(x)).split('.')[1]) for x in list_sizes])

    # MEDIAS EXP HISTORICAS
    fechas = [x for x in df_tot[cons.TIME_1]]

    # ### PINTAR GRAFICAS ###
    if param.GRAFICA:
        df_hist_exp = df_medias_bids_asks(asks, param.CRYPTO, fechas, param.N_RAPIDA_ASKS, param.N_LENTA_ASKS)
        pintar_grafica(df_hist_exp, param.CRYPTO)
    else:
        pass

    # IDENTIFICACION DE TRAMOS DE INVERSION Y DEL TRAMO INSTANTANEO
    # lista_maximos_records = db.lista_maximos_records
    lista_maximos_records = [95000]  # LEER DE LA BBDD
    precio_instantaneo = df_tot[cons.BIDS_1].iloc(0)[-1]
    valor_max_tiempo_real = df_tot[cons.BIDS_1].max()
    tramo_actual = tramo_inv(param.CRYPTO,
                             param.N_TRAMOS,
                             lista_maximos_records,
                             precio_instantaneo,
                             valor_max_tiempo_real)  # FALTA TOMAR LA LISTA DE MAXIMOS DE LA BBDD

    # # LECTURA BBDD-LAST_BUY
    # records_ultima_compra = db.ultima_compra_records
    # last_buy_trigg = trigger_list_last_buy(records_ultima_compra, trigger_tramos, tramo_actual[0], eur,
    #                                        inversion_fija_eur)
    # lista_last_buy = last_buy_trigg[0]
    # lista_last_sell = last_buy_trigg[1]
    # orden_filled_size = last_buy_trigg[2]
    # trigger = last_buy_trigg[3]

    ### Inicializacion y medias_exp ###
    medias_exp_rapida_bids = [medias_exp(bids[-2 * param.N_LENTA_BIDS:], param.N_RAPIDA_BIDS, param.N_LENTA_BIDS)[0][-1]]
    medias_exp_lenta_bids = [medias_exp(bids[-2 * param.N_LENTA_BIDS:], param.N_RAPIDA_BIDS, param.N_LENTA_BIDS)[1][-1]]
    medias_exp_rapida_asks = [medias_exp(asks[-2 * param.N_LENTA_ASKS:], param.N_RAPIDA_ASKS, param.N_LENTA_ASKS)[0][-1]]
    medias_exp_lenta_asks = [medias_exp(asks[-2 * param.N_LENTA_ASKS:], param.N_RAPIDA_ASKS, param.N_LENTA_ASKS)[1][-1]]

    time.sleep(5)
    t00 = time.perf_counter()

    while True:
        try:
            t0 = time.perf_counter()
            tiempo_transcurrido = time.perf_counter() - t00
            ### BidAsk ###
            try:
                client = RESTClient(api_key=api_key, api_secret=api_secret)
                bidask = client.get_product_book(product_id=param.CRYPTO, limit=1,
                                                 aggregation_price_increment=0.01)["pricebook"]
                ordenes_aux = {cons.BIDS: [[round(float(bidask[cons.BIDS][0][cons.PRICE]), 2),
                                            round(float(bidask[cons.BIDS][0][cons.SIZE]), n_decim_size)]],
                               cons.ASKS: [[round(float(bidask[cons.ASKS][0][cons.PRICE]), 2),
                                            round(float(bidask[cons.ASKS][0][cons.SIZE]), n_decim_size)]],
                               cons.TIME: bidask[cons.TIME]
                               }
                ordenes.append(ordenes_aux)
            except Exception as e:
                crypto_log.info(e)
                pass
            precio_compra_bidask = float(ordenes[-1][cons.BIDS][0][0])
            precio_venta_bidask = float(ordenes[-1][cons.ASKS][0][0])

            # ACTUALIZACION LISTAS PRECIOS, DF_TOT Y MEDIAS_EXP
            time_1 = datetime.datetime.utcnow().replace(tzinfo=None)
            to_union = pd.DataFrame(
                {cons.TIME_1: [time_1], cons.BIDS_1: [precio_compra_bidask], cons.ASKS_1: [precio_venta_bidask]})
            df_tot = pd.concat([df_tot, to_union], ignore_index=True)
            bids.append(precio_compra_bidask)
            asks.append(precio_venta_bidask)

            # TODO - to be continued...
            medias_exp_rapida_bids.append(ema(n_rapida_bids, bids, 2.0 / (n_rapida_bids + 1), medias_exp_rapida_bids))
            medias_exp_lenta_bids.append(ema(n_lenta_bids, bids, 2.0 / (n_lenta_bids + 1), medias_exp_lenta_bids))
            medias_exp_rapida_asks.append(ema(n_rapida_asks, asks, 2.0 / (n_rapida_asks + 1), medias_exp_rapida_asks))
            medias_exp_lenta_asks.append(ema(n_lenta_asks, asks, 2.0 / (n_lenta_asks + 1), medias_exp_lenta_asks))
            ### Limitacion tamaño lista ###
            bids = limite_tamanio(tamanio_listas_min, factor_tamanio, bids)
            asks = limite_tamanio(tamanio_listas_min, factor_tamanio, asks)
            df_tot = limite_tamanio_df(tamanio_listas_min, factor_tamanio, df_tot)
            medias_exp_rapida_bids = limite_tamanio(tamanio_listas_min, factor_tamanio, medias_exp_rapida_bids)
            medias_exp_lenta_bids = limite_tamanio(tamanio_listas_min, factor_tamanio, medias_exp_lenta_bids)
            medias_exp_rapida_asks = limite_tamanio(tamanio_listas_min, factor_tamanio, medias_exp_rapida_asks)
            medias_exp_lenta_asks = limite_tamanio(tamanio_listas_min, factor_tamanio, medias_exp_lenta_asks)
            ### FONDOS_DISPONIBLES ##
            disp_ini = disposiciones_iniciales(api_url, auth)
            try:
                eur = math.trunc(disp_ini['EUR'] * 100) / 100
            except Exception as e:
                crypto_log.info(e)
                eur = 0
                pass
