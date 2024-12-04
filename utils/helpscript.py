#####################
# PETICIONES API-REST
#####################
# # FORMA 1 - CON SDK (Software Development Kit)
# client = RESTClient(api_key=api_key, api_secret=api_secret)
# jwt_token = jwt_generator.build_ws_jwt(api_key, api_secret) # no hace falta pero como lo pongo como info
# accounts = client.get_accounts()[cons.ACCOUNTS]
# accounts_crypto = [x["available_balance"] for x in accounts if x["available_balance"]["value"] != "0"]
# disp_ini = disposiciones_iniciales(client)

# # FORMA 2 - CON API-REST
# request_method = cons.GET
# endpoint = "/api/v3/brokerage/accounts"
# uri = f"{request_method} {cons.REQUEST_HOST}{endpoint}"
# jwt_token = build_jwt(api_key, api_secret, uri)
# headers = {
#     'Content-Type': 'application/json',
#     "Authorization": f"Bearer {jwt_token}"}
# # HTTPCLIENT
# conn = http.client.HTTPSConnection(cons.REQUEST_HOST)
# payload = ''
# conn.request(request_method, endpoint, payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))
# # REQUESTS
# endpoint_path = os.path.join(cons.HTTPS, cons.REQUEST_HOST, endpoint).replace("\\", "/")
# res = rq.get(endpoint_path, headers=headers)
# res.json()

# # Forma 3 - Con clase propia
# endpoint = f"/api/v3/brokerage/products/{crypto}/ticker"
# restapi = RestApi(api_key, api_secret, cons.GET, endpoint, cursor=1)
# jsonresp = restapi.rest()


# #################################
# # #### CONSULTAS RESUMEN #######
# #################################
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


#
# ######################################################
# # BBDD ###############################################
# ######################################################
# # CREACION DDBB
#     cielo = TinyDB('cielo.db')
#     constelacion = cielo.table('constelacion')
#     tablas = cielo.tables()
#
#     constelacion.insert({'nombre': 'Casiopea',
#                          'abrev': 'CAS',
#                          'sup': 598,
#                          'obs': 'To-do el año'})  # 1
#     constelacion.insert({'nombre': 'Cefeo',
#                          'abrev': 'CEP',
#                          'sup': 500,
#                          'obs': 'Todo el año'})  # 2
#     constelacion.insert({'nombre': 'Dragón',
#                          'abrev': 'DRA',
#                          'sup': 1083,
#                          'obs': 'Todo el año'})  # 3
#     constelacion.insert_multiple([{'nombre': 'Casiopea',
#                                    'abrev': 'CAS'},
#                                   {'nombre': 'Cefeo',
#                                    'abrev': 'CEP'}])  # [1,2]
#     constelacion.insert({'nombre': 'Dragón',
#                          'abrev': 'DRA',
#                          'sup': 1083})  # 3
#     constelacion.insert_multiple({'obs': 'invierno',
#                                   'indice': ind} for ind in range(5))
#     registros = constelacion.search(where('indice') != -1)
#     constelacion.all()
#
#     registros = constelacion.all()
#     for registro in registros:
#         print(registro['nombre'],
#               registro['abrev'],
#               registro['sup'],
#               registro['obs'])
#
#     registros = constelacion.search(where('obs') == 'Todo el año')
#     for registro in registros:
#         print(registro['nombre'],
#               registro['abrev'],
#               registro['sup'],
#               registro['obs'])
#
#     try:
#         registros = constelacion.search(where('obs') == 'Todo el mes')
#         print(registros[0]['nombre'],
#               registros[0]['abrev'],
#               registros[0]['sup'],
#               registros[0]['obs'])
#     except IndexError:
#         print("No existen registros")
#
#     constelacion.update({'sup': 588}, where('nombre') == 'Cefeo')
#     constelacion.all()
#
#     constelacion.remove(where('sup') > 590)
#     constelacion.all()
#
# # TO DELETE IN BBDD
#     lista_maximos_records.remove((where(cons.CRYPTO) == cons.BTC_EUR) &
#                                  (where(cons.LISTA_MAXIMOS) == [96000]))
#     lista_maximos_records.remove((where(cons.CRYPTO)==cons.BTC_EUR) | (where(cons.CRYPTO)==cons.ADA_EUR))
#
#     constelacion.purge()
#
#     cielo.purge_tables()
#
#     cielo.close()

# # ordenes compra-venta
# orden_venta = buy_sell(cons.SELL,
#                         param.CRYPTO,
#                         cons.MARKET,
#                         api_key,
#                         api_secret,
#                         str(0.87))  # MARKET SELL

# orden_venta = buy_sell(cons.SELL,
#                         param.CRYPTO,
#                         cons.LIMIT,
#                         api_key,
#                         api_secret,
#                         str(0.88),
#                        str(1.17))  # LIMIT SELL


# # MAIL
# subject_mail = 'CryptoTrading_v1.0 - BUY %s' % param.CRYPTO
# message_mail = 'Compra de %s %s a un precio de %s eur -- variacion maxima instantanea = %s%% -- ' \
#                'phigh = %s eur -- plow = %s eur -- tramo = %s -- id_compra_bbdd = %s' \
#                % (orden_filled_size, param.CRYPTO, precio_venta_bidask,
#                   str(round(porcentaje_inst_tiempo * 100, 2)), str(round(phigh, 5)),
#                   str(round(plow, 5)),
#                   tramo_actual[0], id_compra_bbdd)
# automated_mail(smtp, port, sender, password, receivers, subject_mail, message_mail)
# # WHATSAPP
# message_whatsapp = 'Your CryptoTrading code is BUY_%s_%s_price_%s_eur_variacion_%s%%_tramo_%s_' \
#                    'id_compra_bbdd_%s' \
#                    % (orden_filled_size, crypto, precio_venta_bidask,
#                       str(round(porcentaje_inst_tiempo * 100, 2)), tramo_actual[0],
#                       id_compra_bbdd)
# automated_whatsapp(client_wt, from_phone, message_whatsapp, to_phone)
# crypto_log.info(
#     f'COMPRA!!! precio_compra = {precio_venta_bidask} - phigh = {phigh} - plow = {plow}')
# crypto_log.info(porcentaje_inst_tiempo * 100)
# # TWITTER
# message_twitter = f'Hi!! ivcryptotrading BOT has bought {inversion_fija_eur} ' \
#                   f'eur in {orden_filled_size} {crypto_short} at a price {precio_venta_bidask} ' \
#                   f'eur/{crypto_short} #crypto ' \
#                   f'@ivquantic @CoinbasePro @coinbase @bit2me @elonmusk @MundoCrypto_ES ' \
#                   f'@healthy_pockets @wallstwolverine'
# if trigger_twitter:
#     api.update_status(message_twitter)
