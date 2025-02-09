# PARAMETERS

INVERSION_FIJA_EUR = 200  # cantidad en eur maximo por operación
DELETE_LOGS = False
TIME_PAUSAS_LOGS = 600
TIME_CONDICIONES_COMPRAVENTA_LOGS = 600
T_COMPRA_LIMIT = 5  # seconds
T_VENTA_LIMIT = 5  # seconds
PORCENTAJE_INST_TIEMPO = 0.0  # valor constante en caso de error

API_URL = 'https =//api.coinbase.com/api/v3/brokerage/'

TRIGGER_TWITTER = True  # Para activar/desactivar mandar twitts en twitter
TRIGGER_GMAIL = True  # Para activar/desactivar mandar twitts en twitter

BTC_EUR = "BTC-EUR"
ETH_EUR = "ETH-EUR"
ADA_EUR = "ADA-EUR"
LTC_EUR = "LTC-EUR"
XTZ_EUR = "XTZ-EUR"

CRYPTO = ETH_EUR  # producto

MARKET = False
GRAFICA = False  # true para que pinte grafica, false para que no la pinte
N_TRAMOS = 4  # Tramos percentiles

T_LIMIT_PERCENTILE = 28800  # tiempo hacia atrás en segundos para calcular los percentiles
PMAX = 70  # percentil superior seguridad - ideal 50
PMIN = 20  # percentil inferior seguridad - ideal 20
MARGENMAX = 0.15  # Margen limite alrededor del maximo historico para operar con seguridad - ideal 0.1

T_HOURS_BACK = 12
FREQ_EXEC = 1  # frecuencia máxima de ejecución por ciclo Hz - ideal 0.5
CONTADOR_CICLOS = 0  # contador de ciclos
FACTOR_TAMANIO = 100  # factor por el que multiplicar el numero de ciclos para limitar tamanio listas

N_RAPIDA_BIDS = 10  # intervalo para el calculo de la media rapida en los bids (compras) utilizado en nuestras ventas de cripto - ideal 15
N_LENTA_BIDS = 30  # intervalo para el calculo de la media lenta en los bids (compras) utilizado en nuestras ventas de cripto - ideal 60
N_RAPIDA_ASKS = 10  # intervalo para el calculo de la media rapida en los asks (ventas) utilizado en nuestras compras de cripto - 15
N_LENTA_ASKS = 90  # intervalo para el calculo de la media lenta en los bids (ventas) utilizado en nuestras compras de cripto - 60
N_MEDIA = 10  # Numero de valores para calcular la media en los porcetajes_variacion_tiempo

TIME_PERCEN_DICC = {"tiempo_caida_max": 21600,  # tiempo máximo de caida en segundos - si estamos rozando maximos historicos - ideal 1800
                    "porcentaje_caida_max": 0.04,  # porcentaje de caída minimo necesario para la compra - si estamos rozando maximos historicos - ideal = 0.06
                    "tiempo_caida_1": 21600,  # tiempo máximo de caida en segundos - ideal 120min = 7200seg
                    "porcentaje_caida_1": 0.03,  # porcentaje de caída minimo necesario para la compra - ideal 0.04
                    "tiempo_caida_2": 14400,  # tiempo máximo de caida en segundos - ideal 900
                    "porcentaje_caida_2": 0.02,  # porcentaje de caída minimo necesario para la compra - ideal 0.04
                    "tiempo_caida_min": 21600,  # tiempo máximo de caida en segundos - si estamos en condiciones ideales 900 seg
                    "porcentaje_caida_min": 0.02,  # porcentaje de caída minimo necesario para la compra - si estamos en condiciones ideales - ideal 0.05
                    "tiempo_caida_stop": 7200,  # tiempo stop de caida en segundos - si estamos en situacion de stoploss
                    "porcentaje_caida_stop": 0.07,  # porcentaje de caída minimo necesario para la compra - si estamos en situacion de stoploss
                    "porcentaje_beneficio_max": 0.015,  # porcentaje mínimo de beneficio en situacion ideal - ideal 0.02
                    "porcentaje_beneficio_min": 0.010  # porcentaje mínimo de beneficio en situacion extrema, para minimizar riesgo 0.015
                    }

# # OLD
# CRYPTO_TRADING_DB = 'crypto_trading_db'
# WHATSAPP_TWILIO_DB = 'whatsapp_twilio_db'
# MAIL_DB = 'mail_db'
# TWITTER_DB = 'twitter_db'

# NUMMAX = 9999999  # Inicializacion listas
# STOPLOSSMARKER = False  # Para activar el stoploss poner a True (le entra a la funcion stoploss para activarla)
# STOPTRIGGER = False  # Para marcar si estamos en situación de stoploss y poder cambiar condiciones de compra y venta
# PORCENTAJE_LIMITE_STOPLOSS = 0.2  # porcentaje de caída para stoploss - ideal 0.20
# MARGENTRAMO = 0.05  # Margen limite alrededor de cada maximo
# PAG_HISTORIC = 50  # paginas para contar hacia atras y reconstruir historico, cada pag son 100 resultados - ideal 50

# # Inversion por tramos
# TRIGGER_TRAMOS = True  # Para activar la inversion por tramos
# REDEFINICION_MAX = True  # Para activar la redefinicion del maximo segun tramos

# # Lista csv e inversion fija mensual ##
# ACTIVACION_INVERSION_FIJA = False  # Boolean para activar o desactivar la inversion mensual fija
# EUR_INVERSION = 100  # euros de inversion fija mensual
# DICC_CRYPTO = {'BTC-EUR': 0.15,
#                'ETH-EUR': 0.15,
#                'ADA-EUR': 0.15,
#                'SOL-EUR': 0.1,
#                'DOT-EUR': 0.1,
#                'XTZ-EUR': 0.1,
#                'LINK-EUR': 0.04,
#                'XLM-EUR': 0.04,
#                'LTC-EUR': 0.05,
#                'OMG-EUR': 0.04,
#                'UMA-EUR': 0.04,
#                'EOS-EUR': 0.04
#                }
#
# LISTA_CRIPTOS_CSV = ['BTC-EUR',
#                      'ETH-EUR',
#                      'ADA-EUR',
#                      'LINK-EUR',
#                      'OMG-EUR',
#                      'UMA-EUR',
#                      'XLM-EUR',
#                      'XTZ-EUR',
#                      'EOS-EUR',
#                      'LTC-EUR',
#                      'BCH-EUR'
#                      ]
