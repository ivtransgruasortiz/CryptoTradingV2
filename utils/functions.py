import pandas as pd
import time
import datetime
import json
import matplotlib.pyplot as plt
import requests as rq
import hmac, hashlib, base64
from requests.auth import AuthBase
from scipy import stats
import tqdm
import dateutil.parser
from dateutil import tz
from statistics import mean
import math
import smtplib
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.tz import *
from string import ascii_lowercase
import numpy as np
import random


# # AUTHENTICATION INTO COINBASE

class CoinbaseExchangeAuth(AuthBase):

    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        # timestamp = datetime.datetime.now().isoformat()
        message = timestamp + str(request.method).upper() + request.path_url + str(request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        # # signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        # signature_b64 = signature.digest().encode('base64').rstrip('\n')
        signature_b64 = base64.b64encode(signature.digest()).decode()
        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'})
        return request


def tiempo_pausa_new(exec_time, freq):
    """
    FUNCION de usuario que nos da la pausa que debe
    tener un programa para ejecutar algo según una frecuencia
    preestablecida p. ejemplo 1/3 (3 ciclos por segundo) etc... al princicipio del blucle se reinicia la variable inicio now()
    """
    pausa = 1 / freq - exec_time
    if pausa < 0:
        pausa = 0
        print("Delayed execution, consider lowering the fixed execution frequency.")
        print(f"fixed_freq = {freq} vs realtime_freq = {round(1 / exec_time, 2)}")
    return pausa


def disposiciones_iniciales(api_url, auth):
    disp_ini = {}
    try:
        account = rq.get(api_url + 'accounts', auth=auth)
        account = account.json()
        for item in account:
            disp_ini.update({item['currency']: float(item['available'])})
    except:
        pass
    return disp_ini


def percentil(dflista, time_percen_dicc, lecturabbddmax, pmax, pmin, margenmax, stoptrigger, t_limit_percentile):
    phigh = stats.scoreatpercentile(sorted(dflista[-t_limit_percentile:]), pmax)
    plow = stats.scoreatpercentile(sorted(dflista[-t_limit_percentile:]), pmin)
    if stoptrigger:
        porcentaje_caida = [time_percen_dicc['porcentaje_caida_stop']]
        tiempo_caida = [time_percen_dicc['tiempo_caida_stop']]
        porcentaje_beneficio = [time_percen_dicc['porcentaje_beneficio_max']]
        cond = zip(porcentaje_caida, tiempo_caida, porcentaje_beneficio)
    elif (dflista[-1] >= phigh) | (abs(lecturabbddmax - dflista[-1]) <= margenmax * lecturabbddmax):
        porcentaje_caida = [time_percen_dicc['porcentaje_caida_max']]
        tiempo_caida = [time_percen_dicc['tiempo_caida_max']]
        porcentaje_beneficio = [time_percen_dicc['porcentaje_beneficio_min']]
        cond = zip(porcentaje_caida, tiempo_caida, porcentaje_beneficio)
    elif (dflista[-1] > plow) & (dflista[-1] < phigh):
        porcentaje_caida = [time_percen_dicc['porcentaje_caida_1'],
                            time_percen_dicc['porcentaje_caida_2']
                            ]
        tiempo_caida = [time_percen_dicc['tiempo_caida_1'],
                        time_percen_dicc['tiempo_caida_2']
                        ]
        porcentaje_beneficio = [time_percen_dicc['porcentaje_beneficio_min'],
                                time_percen_dicc['porcentaje_beneficio_min']
                                ]
        cond = zip(porcentaje_caida, tiempo_caida, porcentaje_beneficio)
    else:
        porcentaje_caida = [time_percen_dicc['porcentaje_caida_min']]
        tiempo_caida = [time_percen_dicc['tiempo_caida_min']]
        porcentaje_beneficio = [time_percen_dicc['porcentaje_beneficio_max']]
        cond = zip(porcentaje_caida, tiempo_caida, porcentaje_beneficio)
    return [cond, phigh, plow]


def porcentaje_variacion_inst_tiempo(df, tiempo_atras, n_media, tipo):
    """
    :param df: dataframe con precios y times
    :param tiempo_atras: tiempo que queremos recorrer hacia atrás para comparar en segundos
    :param n_media: para hacer la media de los n_media valores de precio
    ;tipo 'bids_1' or 'asks_1'
    :return: valor de % en tanto por uno de la variación sufrida por el valor (ojo!! en tanto por uno, no en %)
    """
    df_cut = df[df['time_1'] >= (datetime.datetime.utcnow().replace(tzinfo=None) -
                                 datetime.timedelta(seconds=tiempo_atras))]
    df_cut_max = max(df_cut[tipo])
    variacion_max = math.trunc(((df[tipo].iloc[-1] / df_cut_max) - 1) * 10000) / 10000
    return variacion_max


def stoploss(lista_last_buy, precio_instantaneo, porcentaje_limite_stoploss, nummax, stoplossmarker, trigger):
    if (lista_last_buy[-1] != nummax) \
            & (precio_instantaneo < (lista_last_buy[-1] * (1 - porcentaje_limite_stoploss))) \
            & stoplossmarker \
            & (not trigger):
        stop = True
    else:
        stop = False
    return stop


def condiciones_buy_sell(precio_compra_bidask, precio_venta_bidask, porcentaje_caida_1, porcentaje_beneficio_1,
                         tipo, trigger, last_buy, medias_exp_rapida_bids, medias_exp_lenta_bids,
                         medias_exp_rapida_asks, medias_exp_lenta_asks, porcentaje_inst_tiempo):
    condicion_media_compra = medias_exp_rapida_asks[-1] > medias_exp_lenta_asks[-1]
    condicion_media_venta = medias_exp_rapida_bids[-1] < medias_exp_lenta_bids[-1]
    if (tipo == 'buy') & trigger & condicion_media_compra & (porcentaje_inst_tiempo < -porcentaje_caida_1):
        condicion = True
        precio = precio_venta_bidask
        print('buy')
    elif (tipo == 'sell') & (not trigger) & condicion_media_venta & \
            (precio_compra_bidask > last_buy[-1] * (1 + porcentaje_beneficio_1)):
        condicion = True
        precio = precio_compra_bidask
        print('sell')
    else:
        condicion = False
        precio = None
    return [condicion, precio]


def buy_sell(compra_venta, crypto, tipo, api_url, auth, sizefunds=None, precio=None):
    '''
        :param compra_venta: 'buy' or 'sell'
        :param crypto: El producto de que se trate
        :param sum_conditions: True or False, trigger para el lanzamiento si se cumplen condiciones
        :param size_order_bidask: tamaño orden
        :param precio_venta_bidask: precio al que se quiere comprar
        :param tipo: market or limit, por defecto, limit (market es para no especificar precio)
        :param api_url: url de conexion
        :param auth: auth de conexion
        :return:
    '''

    if tipo == 'limit':
        size_or_funds = 'size'
    elif tipo == 'market':
        size_or_funds = 'funds'
    if compra_venta == 'buy':
        order = {
            'type': tipo,
            size_or_funds: sizefunds,
            "price": precio,
            "side": compra_venta,
            "product_id": crypto
        }
    elif compra_venta == 'sell':
        size_or_funds = 'size'
        order = {
            'type': tipo,
            size_or_funds: sizefunds,
            "price": precio,
            "side": compra_venta,
            "product_id": crypto
        }
    try:
        # r = rq.post(api_url + 'orders', json=order_buy, auth=auth) ##old
        r = rq.post(api_url + 'orders', data=json.dumps(order), auth=auth)
        ordenes = r.json()
    except:
        time.sleep(0.1)
        ordenes = []
        print('error')
        pass
    return ordenes


def historic_df(crypto, api_url, auth, pag_historic):
    vect_hist = {}
    df_new = pd.DataFrame()
    print('### Gathering Data... ')
    r = rq.get(api_url + 'products/' + crypto + '/trades', auth=auth)
    enlace = r.headers['Cb-After']
    trades = [{'bids': [[float(x['price']), float(x['size']), 1]],
               'asks': [[float(x['price']), float(x['size']), 1]],
               'sequence': x['trade_id'],
               'time': x['time']} for x in r.json()]
    for i in tqdm.trange(pag_historic):
        r = rq.get(api_url + 'products/' + crypto + '/trades?after=%s' % enlace, auth=auth)
        time.sleep(0.3)
        enlace = r.headers['Cb-After']
        valores = r.json()
        # trades = trades + [float(x['price']) for x in r.json()]
        trades += [{'bids': [[float(x['price']), float(x['size']), 1]],
                    'asks': [[float(x['price']), float(x['size']), 1]],
                    'sequence': x['trade_id'],
                    'time': x['time'],
                    'side': x['side']} for x in r.json()]
    df_new = pd.DataFrame.from_dict(trades)
    hist_df = df_new.sort_values('time')
    return hist_df


def sma(n, datos):
    if (len(datos) > n):
        media = sum(datos[-n:]) / n
        return round(media, 5)
    else:
        return round(datos[0], 5)


def ema(n, datos, alpha, media_ant):
    if len(datos) > n:
        expmedia = datos[-1] * alpha + (1 - alpha) * media_ant[-1]
        return round(expmedia, 5)
    else:
        return round(datos[0], 5)


def medias_exp(bids_asks, n_rapida=60, n_lenta=360):
    '''
    :param bids_asks: lista de valores sobre los que calcular las medias exponenciales
    :param n_rapida: periodo de calculo media rapida-nerviosa
    :param n_lenta: periodo de calculo media lenta-tendencia
    :return: lista de listas de valores correspondientes a las medias rapida y lenta
    '''
    mediavar_rapida = []
    mediavar_lenta = []
    expmediavar_rapida = []
    expmediavar_lenta = []
    for i in range(len(bids_asks)):
        mediavar_rapida.append(sma(n_rapida, bids_asks[:i + 1]))
        mediavar_lenta.append(sma(n_lenta, bids_asks[:i + 1]))
        if len(expmediavar_rapida) <= n_rapida + 1:
            expmediavar_rapida.append(mediavar_rapida[-1])
        else:
            expmediavar_rapida.append(ema(n_rapida, bids_asks[:i + 1], 2.0 / (n_rapida + 1), expmediavar_rapida))

        if len(expmediavar_lenta) <= n_lenta + 1:
            expmediavar_lenta.append(mediavar_lenta[-1])
        else:
            expmediavar_lenta.append(ema(n_lenta, bids_asks[:i + 1], 2.0 / (n_lenta + 1), expmediavar_lenta))
    return [expmediavar_rapida, expmediavar_lenta]


def df_medias_bids_asks(bids_asks, crypto, fechas, n_rapida=60, n_lenta=360):
    '''
    :param bids_asks: lista para formar el dataframe
    :param crypto: moneda
    :param fechas: lista fechas
    :param n_rapida: parametros medias para calculos medias exponenciales
    :param n_lenta: parametros medias para calculos medias exponenciales
    :return:
    '''
    df_bids_asks = pd.DataFrame(fechas)
    df_bids_asks['expmedia_rapida'] = medias_exp(bids_asks, n_rapida, n_lenta)[0]
    df_bids_asks['expmedia_lenta'] = medias_exp(bids_asks, n_rapida, n_lenta)[1]
    df_bids_asks[crypto] = bids_asks
    df_bids_asks['time'] = fechas
    return df_bids_asks


def limite_tamanio(tamanio_listas_min, factor_tamanio, lista_a_limitar):
    if len(lista_a_limitar) > tamanio_listas_min * factor_tamanio:
        lista_a_limitar.pop(0)
    return lista_a_limitar


def limite_tamanio_df(tamanio_listas_min, factor_tamanio, df_a_limitar):
    if len(df_a_limitar) > tamanio_listas_min * factor_tamanio:
        df_a_limitar = df_a_limitar.iloc[1:]
    return df_a_limitar


def pintar_grafica(df, crypto):
    '''
    :param df: dataframe a pintar con columnas (fecha, valores1, valores2)
    :param crypto: Moneda
    :return: grafica
    '''
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111)
    plt.plot(df['time'].values, df[crypto], label=crypto)
    ax2.plot(df['time'].values, df['expmedia_rapida'], label='expmedia_rapida')
    ax2.plot(df['time'].values, df['expmedia_lenta'], label='expmedia_lenta')
    ax2.legend()
    plt.xticks(rotation='45')
    plt.show()


def automated_mail(smtp, port, sender, password, receivers, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receivers
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP(smtp, port)
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        response = "Successfully sent Email"
        server.quit()
    # except SMTPException:
    except Exception as e:
        response = "Error: unable to send Email"
        print(e)
    return print(response)


def automated_whatsapp(client, from_phone, body, to_phone):
    # MESSAGE schema well formed:
    # Your {{1}} code is {{2}}
    # Your appointment is coming up on {{1}} at {{2}}
    # Your {{1}} order of {{2}} has shipped and should be delivered on {{3}}. Details: {{4}}
    try:
        message = client.messages.create(
            from_=from_phone,
            body=body,
            to=to_phone
        )
        response = "Successfully sent Whatsapp - Id: " + message.sid
    except:
        response = "Error: unable to send Whatsapp"
    return print(response)


def toma_1(df):
    primero = df[0][0]
    return primero


def fechas_time(df):
    fecha = dateutil.parser.parse(df)
    ### fecha = fecha.replace(tzinfo=None)
    ### fecha = fecha.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    ### fecha = fecha.replace(tzinfo=None).astimezone(tz=None)
    to_zone = tz.tzlocal()
    fecha = fecha.astimezone(to_zone).replace(tzinfo=None)
    return fecha


def tramo_inv(crypto, n_tramos, lista_maximos_records, precio_instantaneo, valor_max_tiempo_real):
    """
    :param crypto: criptomoneda, de la variable crypto
    :param n_tramos: numero de tramos de inversion
    :param lista_maximos_records: lista de maximos de la bbdd de mongo
    :param precio_instantaneo: precio instantaneo a evaluar en que tramo estamos
    :param valor_max_tiempo_real: valor maximo para mockear en caso de no haber datos en bbdd - max del historico
    :return:
    """
    try:
        lista_maximos = list(lista_maximos_records.find({'crypto': crypto}, {"_id": 0}))[0]['lista_maximos']
        lecturabbddmax = max(max(lista_maximos), precio_instantaneo)
        lista_tramos = [lecturabbddmax]
        for item in range(1, n_tramos + 1):
            exec(f'tramo_{item} = round({lecturabbddmax} - ({item}*{lecturabbddmax}*1/{n_tramos}), 2)')
            lista_tramos.append(eval(f'tramo_{item}'))
            if (precio_instantaneo > eval(f'tramo_{item}')) & (precio_instantaneo <= lista_tramos[-2]):
                tramo_actual = f'tramo_{item}'
            else:
                pass
    except Exception as e:
        print(e)
        lecturabbddmax = max(valor_max_tiempo_real, precio_instantaneo)
        for item in range(1, n_tramos + 1):
            exec(f'tramo_{item} = round({lecturabbddmax} - ({item}*{lecturabbddmax}*1/{n_tramos}), 2)')
            lista_tramos.append(eval(f'tramo_{item}'))
            if (precio_instantaneo > eval(f'tramo_{item}')) & (precio_instantaneo <= lista_tramos[-2]):
                tramo_actual = f'tramo_{item}'
            else:
                pass
        pass
    # print(lista_tramos)
    return [tramo_actual, lista_tramos]


def trigger_list_last_buy(records, trigger_tramos, tramo_actual, eur, inversion_fija_eur):
    """
    :param records: el json con la lectura de la bbdd
    :param trigger_tramos: trigger para activacion o no de los tramos
    :param tramo_actual: el tramo en el que esta situado el precio actual
    :param eur: eur disponibles en la cuenta
    :param inversion_fija_eur: cantidad fija que se invierte en la compra
    :return: una lista con varios elementos
    """
    nummax = 9999999
    lista_last_buy = list(records.find({}, {"_id": 0}))
    if trigger_tramos:
        lista_last_buy = [x for x in lista_last_buy if tramo_actual == x['tramo']]
    if (lista_last_buy == []) & (eur >= inversion_fija_eur):
        orden_filled_size = 0
        lista_last_buy = [nummax]
        lista_last_sell = [nummax]
        trigger = True
    elif lista_last_buy != []:
        try:
            orden_filled_size = lista_last_buy[-1]['orden_filled_size']
            lista_last_buy = [lista_last_buy[-1]['last_buy']]
        except Exception as e:
            print(e)
            orden_filled_size = 0
            lista_last_buy = [nummax]
        lista_last_sell = [nummax]
        trigger = False
    else:
        lista_last_buy = [nummax]
        lista_last_sell = [nummax]
        orden_filled_size = 0
        trigger = False
    return [lista_last_buy, lista_last_sell, orden_filled_size, trigger]


def random_name():
    a = np.random.random(15) * 10
    letters = {letter: str(index) for index, letter in enumerate(ascii_lowercase, start=1)}
    b = [list(letters.keys())[int(x)].upper() for x in a[:5]] + \
        [list(letters.keys())[int(x)].lower() for x in a[:10]] + \
        [str(int(x)) for x in a[10:]]
    random.shuffle(b)
    c = ''.join(b)
    return c


def bool_compras_previas(tramo_actual, records):
    """
    Funcion para determinar si se han realizado compras previas. Si es true, hay que redefinir el max
    :param tramo_actual: lista con tramo actual
    :param records: base de datos de db.ultima_compra_records
    :return: boolean
    """
    lista_prev_buy = list(records.find({}, {"_id": 0}))
    lista_prev_buy = [x for x in lista_prev_buy if x['tramo'] != tramo_actual]
    if not lista_prev_buy:
        boolbuy = False
    else:
        boolbuy = True
    return boolbuy
