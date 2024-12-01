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
#     constelacion.purge()
#
#     cielo.purge_tables()
#
#     cielo.close()
