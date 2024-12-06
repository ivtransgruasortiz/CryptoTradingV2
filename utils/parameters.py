# PARAMETERS
MARKET = True
CRYPTO_TRADING_DB = 'crypto_trading_db'
WHATSAPP_TWILIO_DB = 'whatsapp_twilio_db'
MAIL_DB = 'mail_db'
TWITTER_DB = 'twitter_db'

GRAFICA = True  # true para que pinte grafica, false para que no la pinte
NUMMAX = 9999999  # Inicializacion listas
STOPLOSSMARKER = False  # Para activar el stoploss poner a True (le entra a la funcion stoploss para activarla)
STOPTRIGGER = False  # Para marcar si estamos en situación de stoploss y poder cambiar condiciones de compra y venta
TRIGGER_TWITTER = True  # Para activar/desactivar mandar twitts en twitter
PORCENTAJE_LIMITE_STOPLOSS = 0.2  # porcentaje de caída para stoploss - ideal 0.20
INVERSION_FIJA_EUR = 1  # cantidad en eur maximo por operación
# INVERSION_FIJA_EUR = 2000  # cantidad en eur maximo por operación

# CRYPTO = "BTC-EUR"  # producto
CRYPTO = "ADA-EUR"  # producto

API_URL = 'https =//api.coinbase.com/api/v3/brokerage/'

T_LIMIT_PERCENTILE = 28800  # tiempo hacia atrás en segundos para calcular los percentiles
PMAX = 50  # percentil superior seguridad - ideal 50
PMIN = 10  # percentil inferior seguridad - ideal 20
MARGENMAX = 0.10  # Margen limite alrededor del maximo historico para operar con seguridad - ideal 0.1
MARGENTRAMO = 0.05  # Margen limite alrededor de cada maximo

TIME_PERCEN_DICC = {"tiempo_caida_max": 900,
                    # tiempo máximo de caida en segundos - si estamos rozando maximos historicos - ideal 600
                    "porcentaje_caida_max": 0.05,
                    # porcentaje de caída minimo necesario para la compra - si estamos rozando maximos historicos - ideal = 0.06
                    "tiempo_caida_1": 7200,  # tiempo máximo de caida en segundos - ideal 120min = 7200seg
                    "porcentaje_caida_1": 0.04,  # porcentaje de caída minimo necesario para la compra - ideal 0.04
                    "tiempo_caida_2": 1800,  # tiempo máximo de caida en segundos - ideal 120min = 7200seg
                    "porcentaje_caida_2": 0.03,  # porcentaje de caída minimo necesario para la compra - ideal 0.04
                    "tiempo_caida_min": 1200,
                    # tiempo máximo de caida en segundos - si estamos en condiciones ideales 900 seg
                    "porcentaje_caida_min": 0.02,
                    # porcentaje de caída minimo necesario para la compra - si estamos en condiciones ideales - ideal 0.05
                    "tiempo_caida_stop": 7200,  # tiempo stop de caida en segundos - si estamos en situacion de stoploss
                    "porcentaje_caida_stop": 0.07,
                    # porcentaje de caída minimo necesario para la compra - si estamos en situacion de stoploss
                    "porcentaje_beneficio_max": 0.02,  # porcentaje mínimo de beneficio en situacion ideal - ideal 0.02
                    "porcentaje_beneficio_min": 0.015
                    # porcentaje mínimo de beneficio en situacion extrema, para minimizar riesgo 0.015
                    }

PAG_HISTORIC = 50  # paginas para contar hacia atras y reconstruir historico, cada pag son 100 resultados - ideal 50
T_HOURS_BACK = 6
FREQ_EXEC = 0.5  # frecuencia máxima de ejecución por ciclo Hz - ideal 0.5
CONTADOR_CICLOS = 0  # contador de ciclos
FACTOR_TAMANIO = 100  # factor por el que multiplicar el numero de ciclos para limitar tamanio listas

N_RAPIDA_BIDS = 15  # intervalo para el calculo de la media rapida en los bids (compras) utilizado en nuestras ventas de cripto - ideal 15
N_LENTA_BIDS = 30  # intervalo para el calculo de la media lenta en los bids (compras) utilizado en nuestras ventas de cripto - ideal 60
N_RAPIDA_ASKS = 30  # intervalo para el calculo de la media rapida en los asks (ventas) utilizado en nuestras compras de cripto - 10
N_LENTA_ASKS = 90  # intervalo para el calculo de la media lenta en los bids (ventas) utilizado en nuestras compras de cripto - 40
N_MEDIA = 10  # Numero de valores para calcular la media en los porcetajes_variacion_tiempo

## Inversion por tramos
TRIGGER_TRAMOS = True  # Para activar la inversion por tramos
N_TRAMOS = 4
REDEFINICION_MAX = True  # Para activar la redefinicion del maximo segun tramos

## Lista csv e inversion fija mensual ##
ACTIVACION_INVERSION_FIJA = False  # Boolean para activar o desactivar la inversion mensual fija
EUR_INVERSION = 100  # euros de inversion fija mensual
DICC_CRYPTO = {'BTC-EUR': 0.15,
               'ETH-EUR': 0.15,
               'ADA-EUR': 0.15,
               'SOL-EUR': 0.1,
               'DOT-EUR': 0.1,
               'XTZ-EUR': 0.1,
               'LINK-EUR': 0.04,
               'XLM-EUR': 0.04,
               'LTC-EUR': 0.05,
               'OMG-EUR': 0.04,
               'UMA-EUR': 0.04,
               'EOS-EUR': 0.04
               }

LISTA_CRIPTOS_CSV = ['BTC-EUR',
                     'ETH-EUR',
                     'ADA-EUR',
                     'LINK-EUR',
                     'OMG-EUR',
                     'UMA-EUR',
                     'XLM-EUR',
                     'XTZ-EUR',
                     'EOS-EUR',
                     'LTC-EUR',
                     'BCH-EUR'
                     ]
