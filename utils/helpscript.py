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
