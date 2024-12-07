import ast
import hashlib
import logging
import re
import json

import math
import os
import ssl
import sys
import time

from coinbase.websocket import WSClient
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
    encrypt, decrypt, fechas_time_utc, ema, limite_tamanio, limite_tamanio_df, trigger_list_last_buy, \
    bool_compras_previas, percentil, porcentaje_variacion_inst_tiempo, condiciones_buy_sell, buy_sell, random_name, \
    stoploss, tiempo_pausa_new, on_message

if __name__ == "__main__":
    # MANAGE LOGGING INFO-FILES
    delete_logs = param.DELETE_LOGS
    if delete_logs:
        archivo = open('cryptologs.log', 'w')
        archivo.close()
    logging.basicConfig(format='%(asctime)s %(name)s-%(levelname)s:: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)
    crypto_log = logging.getLogger("Crypto_Logging")
    formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s:: %(message)s')
    file_handler = logging.FileHandler('cryptologs.log')
    file_handler.setFormatter(formatter)
    crypto_log.addHandler(file_handler)
    # stdout_handler = logging.StreamHandler(sys.stdout)
    # stdout_handler.setFormatter(formatter)
    # crypto_log.addHandler(stdout_handler)
    crypto_log.info("START POINT!!")

    # PARA CAMBIAR EL COMPORTAMIENTO DE LOS PRINT -- SIN ESTA LÍNEA LOS ESCRIBE DEL TIRÓN...
    sys.stdout.flush()

    # PANDAS OPTIONS
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 20)

    try:
        local_execution = ast.literal_eval(os.environ.get(cons.LOCAL_EXECUTION))
    except Exception as e1:
        local_execution = False
        crypto_log.info(f"INFO: local_execution = False - {e1}")
        print(f"INFO: local_execution = False - {e1}")

    if local_execution:
        crypto_log.info(f"INFO!! - Executing in local mode")
        print(f"INFO!! - Executing in local mode")
        passphrase = os.getenv(cons.PASSPHRASE)
    else:
        crypto_log.info(f"INFO!! - Executing in host mode")
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
    contador_ciclos = param.CONTADOR_CICLOS

    # CLIENT API
    client = RESTClient(api_key=api_key, api_secret=api_secret)

    # fees - TASAS COINBASE SEGUN MOVIMIENTOS
    fees = client.get_transaction_summary()
    fees_pricing_tier = fees[cons.FEE_TIER][cons.PRICING_TIER]
    fees_taker = round(float('%.4f' % (float(fees[cons.FEE_TIER][cons.TAKER_FEE_RATE]))), 4)
    fees_maker = round(float('%.4f' % (float(fees[cons.FEE_TIER][cons.MAKER_FEE_RATE]))), 4)
    fees_client = fees_taker if param.MARKET else fees_maker

    # HISTORICO MEJORADO PARA EL SCRIPT
    hist_df = historic_df_sdk(api_key, api_secret, crypto=param.CRYPTO, t_hours_back=param.T_HOURS_BACK, limit=1000)
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

    precio_instantaneo = df_tot[cons.BIDS_1].iloc(0)[-1]
    valor_max_tiempo_real = df_tot[cons.BIDS_1].max()

    # MAXIMO NUMERO DE DECIMALES
    list_prices = [x for x in list(hist_df[cons.PRICE].values) if "." in str(x)]
    n_decim_price = max([len(str(float(x)).split('.')[1]) for x in list_prices])
    list_sizes = [x for x in list(hist_df[cons.SIZE].values) if "." in str(x)]
    n_decim_size = max([len(str(float(x)).split('.')[1]) for x in list_sizes])

    # MEDIAS EXP HISTORICAS
    fechas = [x for x in df_tot[cons.TIME_1]]

    # OBTENEMOS LAS DISPOSICIONES INICIALES DE LA CUENTA
    disp_ini_sdk = get_accounts_sdk(api_key, api_secret)
    eur = math.trunc(disp_ini_sdk[cons.EUR] * 100) / 100
    crypto_quantity = round(disp_ini_sdk[crypto_short], n_decim_size)

    # PINTAR GRAFICAS
    if param.GRAFICA:
        df_hist_exp = df_medias_bids_asks(asks, param.CRYPTO, fechas, param.N_RAPIDA_ASKS, param.N_LENTA_ASKS)
        pintar_grafica(df_hist_exp, param.CRYPTO)
    else:
        pass

    # CREACION-LECTURA DDBBs
    cryptodb = TinyDB(cons.CRYPTODB)
    cryptodb_tables = cryptodb.tables()
    lista_maximos_records = cryptodb.table(cons.LISTA_MAXIMOS_RECORDS)
    records_ultima_compra = cryptodb.table(cons.ULTIMA_COMPRA_RECORDS)
    all_trades_records = cryptodb.table(cons.ALL_TRADES_RECORDS)

    if lista_maximos_records.all() == []:
        for crypto in cons.MAX_DICC.keys():
            lista_maximos_records.upsert({cons.CRYPTO: crypto,
                                          cons.LISTA_MAXIMOS: [cons.MAX_DICC[crypto]]},
                                         where(cons.CRYPTO) == crypto)
    else:
        for crypto in cons.MAX_DICC.keys():
            if crypto not in [x[cons.CRYPTO] for x in lista_maximos_records.all()]:
                print(crypto)
                lista_maximos_records.upsert({cons.CRYPTO: crypto,
                                              cons.LISTA_MAXIMOS: [cons.MAX_DICC[crypto]]},
                                             where(cons.CRYPTO) == crypto)

    # INICIALIZACION Y MEDIAS_EXP
    medias_exp_rapida_bids = [medias_exp(bids[-2 * param.N_LENTA_BIDS:],
                                         param.N_RAPIDA_BIDS,
                                         param.N_LENTA_BIDS)[0][-1]]
    medias_exp_lenta_bids = [medias_exp(bids[-2 * param.N_LENTA_BIDS:],
                                        param.N_RAPIDA_BIDS,
                                        param.N_LENTA_BIDS)[1][-1]]
    medias_exp_rapida_asks = [medias_exp(asks[-2 * param.N_LENTA_ASKS:],
                                         param.N_RAPIDA_ASKS,
                                         param.N_LENTA_ASKS)[0][-1]]
    medias_exp_lenta_asks = [medias_exp(asks[-2 * param.N_LENTA_ASKS:],
                                        param.N_RAPIDA_ASKS,
                                        param.N_LENTA_ASKS)[1][-1]]

    time.sleep(5)
    t00 = time.perf_counter()
    t_ciclo_medio_list = []

    while True:
        try:
            t0 = time.perf_counter()
            tiempo_transcurrido = time.perf_counter() - t00

            # BIDASK
            try:
                client = RESTClient(api_key=api_key, api_secret=api_secret)
                bidask = client.get_product_book(product_id=param.CRYPTO, limit=1,
                                                 aggregation_price_increment=10 ** (-n_decim_price))[cons.PRICEBOOK]
                ordenes_aux = {cons.BIDS: [[round(float(bidask[cons.BIDS][0][cons.PRICE]), n_decim_price),
                                            round(float(bidask[cons.BIDS][0][cons.SIZE]), n_decim_size)]],
                               cons.ASKS: [[round(float(bidask[cons.ASKS][0][cons.PRICE]), n_decim_price),
                                            round(float(bidask[cons.ASKS][0][cons.SIZE]), n_decim_size)]],
                               cons.TIME: bidask[cons.TIME]
                               }
                ordenes.append(ordenes_aux)
            except Exception as e:
                crypto_log.info(e)
                pass
            precio_compra_bidask = float(ordenes[-1][cons.BIDS][0][0])
            precio_venta_bidask = float(ordenes[-1][cons.ASKS][0][0])
            precio_compra_limit = precio_venta_bidask - 1 * 10 ** -n_decim_price
            precio_venta_limit = precio_compra_bidask + 1 * 10 ** -n_decim_price

            # ACTUALIZACION LISTAS PRECIOS, DF_TOT Y MEDIAS_EXP
            time_1 = datetime.datetime.utcnow().replace(tzinfo=None)
            to_union = pd.DataFrame(
                {cons.TIME_1: [time_1], cons.BIDS_1: [precio_compra_bidask], cons.ASKS_1: [precio_venta_bidask]})
            df_tot = pd.concat([df_tot, to_union], ignore_index=True)
            bids.append(precio_compra_bidask)
            asks.append(precio_venta_bidask)

            medias_exp_rapida_bids.append(ema(param.N_RAPIDA_BIDS, bids, 2.0 / (param.N_RAPIDA_BIDS + 1),
                                              medias_exp_rapida_bids))
            medias_exp_lenta_bids.append(ema(param.N_LENTA_BIDS, bids, 2.0 / (param.N_LENTA_BIDS + 1),
                                             medias_exp_lenta_bids))
            medias_exp_rapida_asks.append(ema(param.N_RAPIDA_ASKS, asks, 2.0 / (param.N_RAPIDA_ASKS + 1),
                                              medias_exp_rapida_asks))
            medias_exp_lenta_asks.append(ema(param.N_LENTA_ASKS, asks, 2.0 / (param.N_LENTA_ASKS + 1),
                                             medias_exp_lenta_asks))

            # LIMITACION TAMAÑO LISTA
            bids = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, bids)
            asks = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, asks)
            df_tot = limite_tamanio_df(tamanio_listas_min, param.FACTOR_TAMANIO, df_tot)
            medias_exp_rapida_bids = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, medias_exp_rapida_bids)
            medias_exp_lenta_bids = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, medias_exp_lenta_bids)
            medias_exp_rapida_asks = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, medias_exp_rapida_asks)
            medias_exp_lenta_asks = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, medias_exp_lenta_asks)
            t_ciclo_medio_list = limite_tamanio(tamanio_listas_min, param.FACTOR_TAMANIO, t_ciclo_medio_list)

            # FONDOS_DISPONIBLES
            disp_ini_sdk = get_accounts_sdk(api_key, api_secret)
            try:
                eur = math.trunc(disp_ini_sdk[cons.EUR] * 100) / 100
                crypto_quantity = round(disp_ini_sdk[crypto_short], n_decim_size)
            except Exception as e:
                crypto_log.info(e)
                eur = 0
                pass

            # BBDD - ACTUALIZACION MAXIMOS HISTORICOS
            try:
                lista_maximos = lista_maximos_records.search(where(cons.CRYPTO) == param.CRYPTO)[0][cons.LISTA_MAXIMOS]
                lecturabbddmax = max(lista_maximos)
                lecturabbddmedian = math.trunc(np.median(lecturabbddmax) * 100) / 100  # modificado para tomar el maximo
            except Exception as e:
                lista_maximos = []
                lecturabbddmax = precio_venta_bidask
                lecturabbddmedian = math.trunc(precio_venta_bidask * 100) / 100
                lista_maximos.append(precio_venta_bidask)
                lista_maximos_records.insert({cons.CRYPTO: param.CRYPTO, cons.LISTA_MAXIMOS: lista_maximos})
                pass
            if precio_venta_bidask > (lecturabbddmax * 1.02):
                lista_maximos.append(precio_venta_bidask)
                lista_maximos_records.upsert({cons.CRYPTO: param.CRYPTO, cons.LISTA_MAXIMOS: lista_maximos},
                                             where(cons.CRYPTO) == param.CRYPTO)

            # TRAMO_ACTUAL Y TRIGGER PARA COMPRAS
            valor_max_tiempo_real = df_tot[cons.BIDS_1].max()
            tramo_actual = tramo_inv(param.CRYPTO, param.N_TRAMOS, lista_maximos_records, precio_venta_bidask,
                                     valor_max_tiempo_real)
            last_buy_trigg = trigger_list_last_buy(records_ultima_compra)
            lista_last_buy = last_buy_trigg[0]
            lista_last_sell = last_buy_trigg[1]
            orden_filled_size = last_buy_trigg[2]
            trigger = last_buy_trigg[3]

            # AJUSTES DE LOS PARÁMETROS CONDICIONALES DE PORCENTAJE DE CAIDA Y TIEMPOS DE CAIDA
            parametros_caida = percentil(list(df_tot[cons.ASKS_1]), param.TIME_PERCEN_DICC, lecturabbddmedian,
                                         param.PMAX, param.PMIN, param.MARGENMAX, param.T_LIMIT_PERCENTILE)
            zip_param = parametros_caida[0]
            phigh = parametros_caida[1]
            plow = parametros_caida[2]

            # PORCENTAJE DE VARIACION INSTANTANEA
            condiciones_compra_list = []
            porcentaje_beneficio_list = []
            porcentaje_caida = param.TIME_PERCEN_DICC[cons.PORCENTAJE_CAIDA_MIN]
            tiempo_caida = param.TIME_PERCEN_DICC[cons.TIEMPO_CAIDA_MIN]

            dicc_cond_compraventa = []
            for parametros in list(zip_param):
                porcentaje_caida = parametros[0]
                tiempo_caida = parametros[1]
                porcentaje_beneficio = parametros[2]
                try:
                    porcentaje_inst_tiempo = porcentaje_variacion_inst_tiempo(df_tot,
                                                                              tiempo_caida,
                                                                              param.N_MEDIA,
                                                                              cons.ASKS_1)
                except Exception as e:
                    crypto_log.info(e)
                    print('No hay lecturas, df_tot no abarca todo el tiempo considerado')
                    porcentaje_inst_tiempo = 0.01
                    pass

                # COMPRAS
                condiciones_compra = \
                    condiciones_buy_sell(precio_compra_bidask, precio_venta_bidask, porcentaje_caida,
                                         porcentaje_beneficio, cons.BUY, trigger, lista_last_buy,
                                         medias_exp_rapida_bids, medias_exp_lenta_bids,
                                         medias_exp_rapida_asks, medias_exp_lenta_asks,
                                         porcentaje_inst_tiempo, eur, param.INVERSION_FIJA_EUR)
                condiciones_compra_list.append(condiciones_compra[0])
                if condiciones_compra[0]:
                    porcentaje_beneficio_list.append(porcentaje_beneficio)
                else:
                    porcentaje_beneficio_list.append(param.TIME_PERCEN_DICC[cons.PORCENTAJE_BENEFICIO_MIN])
                dicc_cond_compraventa.append(condiciones_compra[2])
            condiciones_compra_total = max(condiciones_compra_list)
            porcentaje_beneficio = max(porcentaje_beneficio_list)

            # ORDEN DE COMPRA
            if condiciones_compra_total:
                crypto_log.info("buy-order sent!!!")
                try:
                    # orden_compra = buy_sell(cons.BUY,
                    #                         param.CRYPTO,
                    #                         cons.MARKET,
                    #                         api_key,
                    #                         api_secret,
                    #                         sizefunds=str(param.INVERSION_FIJA_EUR))  # MARKET BUY
                    orden_compra = buy_sell(cons.BUY,
                                            param.CRYPTO,
                                            cons.LIMIT,
                                            api_key,
                                            api_secret,
                                            sizefunds=str(param.INVERSION_FIJA_EUR),
                                            price_bidask=precio_compra_limit)  # LIMIT BUY
                    limit_order_id = ""
                    order_filled = False
                    ws_client = WSClient(api_key=api_key, api_secret=api_secret, on_message=on_message, verbose=True)
                    ws_client.open()
                    ws_client.subscribe([param.CRYPTO], ["heartbeats", "user"])
                    while not order_filled:
                        ws_client.sleep_with_exception_check(1)
                    crypto_log.info(f"order buy {limit_order_id} filled!")
                    ws_client.close()
                    time.sleep(5)
                    id_compra = orden_compra[cons.RESPONSE][cons.ORDER_ID]
                    id_compra_user = orden_compra[cons.RESPONSE][cons.CLIENT_ORDER_ID]
                    client = RESTClient(api_key=api_key, api_secret=api_secret)
                    orden_detail = client.get_order(order_id=id_compra)
                    orden_filled_size = math.trunc(float(orden_detail[cons.ORDER][cons.FILLED_SIZE])
                                                   * 10 ** n_decim_size) / 10 ** n_decim_size
                    orden_filled_price = math.trunc(float(orden_detail[cons.ORDER][cons.AVERAGE_FILLED_PRICE])
                                                    * 10 ** n_decim_price) / 10 ** n_decim_price
                    orden_fees = math.trunc(float(orden_detail[cons.ORDER][cons.TOTAL_FEES])
                                            * 10 ** n_decim_price) / 10 ** n_decim_price
                    lista_last_buy.append(orden_filled_price)
                    crypto_log.info(orden_compra)
                    trigger = False
                    # BBDDs
                    records_ultima_compra.insert({cons.ID_COMPRA_BBDD: id_compra,
                                                  cons.ID_COMPRA_USER_BBDD: id_compra_user,
                                                  cons.ORDEN_FILLED_SIZE: orden_filled_size,
                                                  cons.ORDEN_FILLED_PRICE: orden_filled_price,
                                                  cons.FEES_EUR_COMPRA: orden_fees,
                                                  cons.FEES_CLIENT: fees_client,
                                                  cons.PORCENTAJE_BENEFICIO: porcentaje_beneficio,
                                                  cons.FECHA: datetime.datetime.now().isoformat(),
                                                  cons.TRAMO: tramo_actual[0]})
                    crypto_log.info(records_ultima_compra.all())
                    all_trades_records.insert(orden_compra)
                except Exception as e:
                    crypto_log.info(e)
                    pass

            # VENTA

            # # STOPLOSS y Condiciones-Venta
            # stop = stoploss(lista_last_buy,
            #                 precio_compra_bidask,
            #                 porcentaje_limite_stoploss,
            #                 nummax,
            #                 stoplossmarker,
            #                 trigger)
            # if stop:
            #     stoptrigger = True

            # BUCLE PARA EJECUTAR TODAS LAS VENTAS SI SE DAN LAS CONDICIONES - PARA TODOS LOS TRAMOS
            lista_last_buy_bbdd = records_ultima_compra.all()
            lista_last_buy_tramo = []
            if not lista_last_buy_bbdd:
                trigger = True
            condiciones_venta_list = []
            for compra in lista_last_buy_bbdd:
                try:
                    trigger = False
                    id_compra_bbdd = compra[cons.ID_COMPRA_BBDD]
                    orden_filled_size = compra[cons.ORDEN_FILLED_SIZE]
                    orden_filled_price = compra[cons.ORDEN_FILLED_PRICE]
                    porcentaje_beneficio = compra[cons.PORCENTAJE_BENEFICIO]
                    tramo_actual_compra = compra[cons.TRAMO]
                except Exception as e:
                    trigger = True
                    id_compra_bbdd = None
                    orden_filled_size = None
                    orden_filled_price = None
                    porcentaje_beneficio = None
                    tramo_actual_compra = None
                    print('Error lectura bbdd')

                # CONDICIONES VENTA
                condiciones_venta = \
                    condiciones_buy_sell(precio_compra_bidask, precio_venta_bidask, porcentaje_caida,
                                         porcentaje_beneficio, cons.SELL, trigger, lista_last_buy,
                                         medias_exp_rapida_bids, medias_exp_lenta_bids,
                                         medias_exp_rapida_asks, medias_exp_lenta_asks,
                                         porcentaje_inst_tiempo)
                condiciones_venta_list.append(condiciones_venta)
                # ORDEN DE VENTA
                if condiciones_venta[0]:
                    crypto_log.info("sell-order sent!!!")
                    try:
                        # orden_venta = buy_sell(cons.SELL,
                        #                        param.CRYPTO,
                        #                        cons.MARKET,
                        #                        api_key,
                        #                        api_secret,
                        #                        str(orden_filled_size))  # MARKET SELL
                        orden_venta = buy_sell(cons.SELL,
                                               param.CRYPTO,
                                               cons.LIMIT,
                                               api_key,
                                               api_secret,
                                               sizefunds=str(orden_filled_size),
                                               price_bidask=precio_venta_limit)  # LIMIT SELL
                        limit_order_id = ""
                        order_filled = False
                        ws_client = WSClient(api_key=api_key, api_secret=api_secret, on_message=on_message,
                                             verbose=True)
                        ws_client.open()
                        ws_client.subscribe([param.CRYPTO], ["heartbeats", "user"])
                        while not order_filled:
                            ws_client.sleep_with_exception_check(1)
                        crypto_log.info(f"order sell {limit_order_id} filled!")
                        ws_client.close()
                        time.sleep(5)
                        id_venta = orden_venta[cons.RESPONSE][cons.ORDER_ID]
                        id_venta_user = orden_venta[cons.RESPONSE][cons.CLIENT_ORDER_ID]
                        client = RESTClient(api_key=api_key, api_secret=api_secret)
                        orden_detail = client.get_order(order_id=id_venta)
                        orden_filled_size = math.trunc(float(orden_detail[cons.ORDER][cons.FILLED_SIZE])
                                                       * 10 ** n_decim_size) / 10 ** n_decim_size
                        orden_filled_price = math.trunc(float(orden_detail[cons.ORDER][cons.AVERAGE_FILLED_PRICE])
                                                        * 10 ** n_decim_price) / 10 ** n_decim_price
                        orden_fees = math.trunc(float(orden_detail[cons.ORDER][cons.TOTAL_FEES])
                                                * 10 ** n_decim_price) / 10 ** n_decim_price
                        lista_last_sell.append(orden_filled_price)
                        crypto_log.info(orden_venta)
                        trigger = True

                        # BBDD
                        records_ultima_compra.remove(where(cons.ID_COMPRA_BBDD) == id_compra_bbdd)
                        all_trades_records.insert(orden_venta)
                    except Exception as e:
                        crypto_log.info(e)
                        pass

            # LOGGING CONDICIONES COMPRA-VENTA Y PAUSAS INFO-GENERAL
            # CALCULO PAUSAS
            contador_ciclos += 1  # para poder comparar hacia atrśs freq*time_required = num_ciclos hacia atras
            time.sleep(tiempo_pausa_new(time.perf_counter() - t0, param.FREQ_EXEC))
            t_ciclo = round(time.perf_counter() - t0, 2)
            t_ciclo_medio_list.append(t_ciclo)
            t_ciclo_medio = np.mean(t_ciclo_medio_list)
            # print(contador_ciclos)
            if contador_ciclos % param.TIME_CONDICIONES_COMPRAVENTA_LOGS == 0:
                crypto_log.info(f"El tiempo transcurrido por ciclo es: {t_ciclo} seg.")
                crypto_log.info(f"El tiempo medio transcurrido por ciclo es: {t_ciclo_medio} seg.")
                crypto_log.info(tramo_actual)
                crypto_log.info(dicc_cond_compraventa)
                crypto_log.info(f"condiciones_compra_total = {condiciones_compra_total}")
                for item in range(len(lista_last_buy_bbdd)):
                    crypto_log.info(f"condiciones_venta_total = {condiciones_venta_list[item]}")

            if contador_ciclos % param.TIME_PAUSAS_LOGS == 0:
                crypto_log.info(f'Numero de ciclos: {contador_ciclos}')
                crypto_log.info(f'Precio compra bidask: {precio_compra_bidask} eur.')
                crypto_log.info(f'Precio venta bidask: {precio_venta_bidask} eur.')
                crypto_log.info(f'phigh: {str(round(phigh, 5))} eur.')
                crypto_log.info(f'plow: {str(round(plow, 5))} eur.')
                crypto_log.info(f'Dif_inst_max: {str(round(porcentaje_inst_tiempo * 100, 2))} %')
        except (KeyboardInterrupt, SystemExit):  # ctrl + c
            crypto_log.info('\n'
                            '############'
                            '\nAll done\n'
                            '############'
                            '\n')
            break
# FIN
# TODO - to be continued...
