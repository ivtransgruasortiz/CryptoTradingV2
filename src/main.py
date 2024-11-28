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

import matplotlib as mpl
import matplotlib.pyplot as plt

import utils.constants as cons
from utils.functions import Headers, get_accounts, get_accounts_sdk, disposiciones_iniciales, \
    historic_df_sdk, toma_1, fechas_time, df_medias_bids_asks, pintar_grafica, medias_exp, sma, tramo_inv

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

    # OBTENEMOS LAS DISPOSICIONES INICIALES DE LA CUENTA
    disp_ini = get_accounts(api_key, api_secret)
    disp_ini_sdk = get_accounts_sdk(api_key, api_secret)
    eur = math.trunc(disp_ini_sdk[cons.EUR] * 100) / 100
    crypto_quantity = math.trunc(disp_ini_sdk[crypto_short] * 100) / 100

    # HISTORICO MEJORADO PARA EL SCRIPT
    # hist_df["bids"] = hist_df[["price", "size"]].to_numpy().tolist()
    hist_df = historic_df_sdk(api_key, api_secret, crypto=cons.BTC_EUR, t_hours_back=3, limit=1000)
    hist_df["bids"] = [[[x, y, z]] for x, y, z in
                       zip(hist_df['price'], hist_df['price'], [1 for x in range(len(hist_df))])]
    hist_df["asks"] = [[[x, y, z]] for x, y, z in
                       zip(hist_df['price'], hist_df['price'], [1 for x in range(len(hist_df))])]
    bids = [x[0][0] for x in list(hist_df['bids'].values)]
    asks = [x[0][0] for x in list(hist_df['asks'].values)]
    ordenes = hist_df[['bids', 'asks', 'trade_id']].to_dict(orient='records')

    # HISTORICO MEJORADO PARA EL SCRIPT
    df_tot = hist_df
    df_tot['bids_1'] = np.vectorize(toma_1)(df_tot['bids'])
    df_tot['asks_1'] = np.vectorize(toma_1)(df_tot['asks'])
    df_tot['time_1'] = np.vectorize(fechas_time)(df_tot['time'])
    df_tot = df_tot.sort_values('time_1', ascending=True).reset_index()
    df_tot = df_tot[['time_1', 'bids_1', 'asks_1']]

    # MAXIMO NUMERO DE DECIMALES
    n_decim = max([len(str(x[0][1]).split('.')[1]) for x in list(hist_df['asks'].values)])

    # MEDIAS EXP HISTORICAS
    fechas = [x for x in df_tot['time_1']]

    # ### PINTAR GRAFICAS ###
    if grafica:
        df_hist_exp = df_medias_bids_asks(asks, crypto, fechas, n_rapida_asks, n_lenta_asks)
        pintar_grafica(df_hist_exp, crypto)
    else:
        pass

    # IDENTIFICACION DE TRAMOS DE INVERSION Y DEL TRAMO INSTANTANEO
    # lista_maximos_records = db.lista_maximos_records
    lista_maximos_records = [95000]  # LEER DE LA BBDD
    precio_instantaneo = df_tot['bids_1'].iloc(0)[-1]
    valor_max_tiempo_real = df_tot['bids_1'].max()
    tramo_actual = tramo_inv(crypto, n_tramos, lista_maximos_records, precio_instantaneo, valor_max_tiempo_real)  # FALTA TOMAR LA LISTA DE MAXIMOS DE LA BBDD

    # ### Lectura BBDD-Last_Buy ###
    # records_ultima_compra = db.ultima_compra_records
    # last_buy_trigg = trigger_list_last_buy(records_ultima_compra, trigger_tramos, tramo_actual[0], eur,
    #                                        inversion_fija_eur)
    # lista_last_buy = last_buy_trigg[0]
    # lista_last_sell = last_buy_trigg[1]
    # orden_filled_size = last_buy_trigg[2]
    # trigger = last_buy_trigg[3]

    ### Inicializacion y medias_exp ###
    medias_exp_rapida_bids = [medias_exp(bids[-2 * n_lenta_bids:], n_rapida_bids, n_lenta_bids)[0][-1]]
    medias_exp_lenta_bids = [medias_exp(bids[-2 * n_lenta_bids:], n_rapida_bids, n_lenta_bids)[1][-1]]
    medias_exp_rapida_asks = [medias_exp(asks[-2 * n_lenta_asks:], n_rapida_asks, n_lenta_asks)[0][-1]]
    medias_exp_lenta_asks = [medias_exp(asks[-2 * n_lenta_asks:], n_rapida_asks, n_lenta_asks)[1][-1]]

    time.sleep(5)
    t00 = time.perf_counter()

    # TODO - to be continued...
    # #prueba TEST
    # contador = 0

    while True:
        try:
            t0 = time.perf_counter()
            tiempo_transcurrido = time.perf_counter() - t00
            ### BidAsk ###
            try:
                bidask = rq.get(api_url + 'products/' + crypto + '/book?level=1')
                bidask = bidask.json()
                ordenes.append(bidask)
            except Exception as e:
                crypto_log.info(e)
                pass
            precio_compra_bidask = float(ordenes[-1]['bids'][0][0])
            precio_venta_bidask = float(ordenes[-1]['asks'][0][0])
            ### Actualizacion listas precios, df_tot y medias_exp ###
            time_1 = datetime.datetime.utcnow().replace(tzinfo=None)
            to_union = pd.DataFrame(
                {'time_1': [time_1], 'bids_1': [precio_compra_bidask], 'asks_1': [precio_venta_bidask]})
            df_tot = df_tot.append(to_union, ignore_index=True)
            bids.append(precio_compra_bidask)
            asks.append(precio_venta_bidask)
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
