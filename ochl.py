
# import needed libraries
# import pandas as pd
# import matplotlib.pyplot as plt
# from pandas_datareader import data as web
from termcolor import colored
import sched, time
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime

os.system('color')

f = open("api.key", "r")
api_key = f.read()
f.close()


state = {'last_action': '', 'last_price':0, 'profit':0, 'datetime': None}

def fetch_price_time():
    url='https://api.polygon.io/v1/last/crypto/DOGE/USD?&apiKey={api_key}'.format(api_key=api_key)
    r = requests.get(url)
    j = r.json()['last']
    return { 'price': j['price'], 'timestamp': j['timestamp'], 'datetime': datetime.fromtimestamp(j['timestamp']/1000) }

def fetchData():
    url='https://api.polygon.io/v2/aggs/ticker/X:DOGEUSD/range/1/minute/2021-02-05/2021-02-05?unadjusted=true&sort=asc&limit=1440&apiKey={api_key}'.format(api_key=api_key)
    r = requests.get(url)
    j = r.json()

    results = j['results']

    for result in results:
        result['date'] = datetime.fromtimestamp(result['t']/1000)

    df = pd.DataFrame.from_dict(results)

    df.set_index('date', inplace=True)

    df['MA20'] = df['c'].rolling(window=20).mean()
    df['20dSTD'] = df['c'].rolling(window=20).std()
    df['upper'] = df['MA20'] + (df['20dSTD'] * 2)
    df['lower'] = df['MA20'] - (df['20dSTD'] * 2)

    # print(df.tail(1))
    return df.tail(1)

s = sched.scheduler(time.time, time.sleep)

def process(sc):
    data = fetchData()
    last_close = data['c'].item()
    last_upper = data['upper'].item()
    last_lower = data['lower'].item()

    last_price_time = fetch_price_time()
    last_price = last_price_time['price']
    last_datetime = last_price_time['datetime']

    if ((last_close > last_upper) and (state['last_action'] == '' or state['last_action'] == 'sell')):
        state['last_price'] = last_price
        state['last_action'] = 'buy'
        state['datetime'] = last_datetime
        print(colored('[{datetime}] BUY DOGE @ {price:.5f}'.format(price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'green'))
        # response = r.order_buy_crypto_by_quantity('DOGE', 100)
    elif (last_close < last_lower and state['last_action'] == 'hold'):
        state['last_action'] = 'sell'
        state['profit'] += last_price - state['last_price']
        state['last_price'] = 0
        print(colored('[{datetime}] SELL DOGE @ {price:.5f}'.format(price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'red'))
        # response = r.order_sell_crypto_by_quantity('DOGE', 100)
    else:
        if (state['last_action'] == 'buy'):
            state['last_action'] = 'hold'
            print(colored('HOLD DOGE @ {price:.5f}'.format(price=last_price), 'yellow'))
        if (state['last_action'] == ''):
            print(colored('[{datetime}] INIT DOGE @ {price:.5f}'.format(price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'blue'))

    s.enter(15, 1, process, (sc,))

s.enter(0, 1, process, (s,))
s.run()



