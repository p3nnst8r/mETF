from termcolor import colored

import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

os.system('color')

f = open("api.key", "r")
api_key = f.read()
f.close()

state = {'last_action': None, 'last_price':0, 'profit':0, 'datetime': None, 'consec_mv_down': 0}

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

def fetch_ochl():
    # r = requests.get('https://api.polygon.io/v2/aggs/ticker/X:DOGEUSD/range/1/minute/2021-02-05/2021-02-05?unadjusted=true&sort=desc&limit=1&apiKey={api_key}'.format(api_key=api_key))
    # j = r.json()
    # results = j['results']
    # print(results)
    None

def process():
    data = fetchData()
    last_open = data['o'].item()
    last_close = data['c'].item()
    last_upper = data['upper'].item()
    last_lower = data['lower'].item()

    if last_close < last_open:
        state['consec_mv_down'] += 1
    else:
        state['consec_mv_down'] = 0

    last_price_time = fetch_price_time()
    last_price = last_price_time['price']
    last_datetime = last_price_time['datetime']

    if ((last_close > last_upper) and (state['last_action'] == None or state['last_action'] == 'sell')):
        state['last_price'] = last_price
        state['last_action'] = 'buy'
        state['datetime'] = last_datetime
        print(colored('[{datetime}] BUY DOGE @ {price:.5f}'.format(price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'green'))
    elif (last_close < last_lower and state['last_action'] == 'hold') or state['consec_mv_down'] >= 3:
        state['consec_mv_down'] = 0
        state['last_action'] = 'sell'
        state['profit'] += last_price - state['last_price']
        state['last_price'] = 0
        print(colored('[{datetime}] SELL DOGE @ {price:.5f} | Session Profit: {session_profit:.5f}'.format(price=last_price, session_profit=state['profit'], datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'red'))
    else:
        if (state['last_action'] == 'buy'):
            state['last_action'] = 'hold'
            # print(colored('{datetime}] HOLD DOGE @ {hold_at:.5f}'.format(hold_at = state['last_price'], price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'yellow'))
        if (state['last_action'] == None):
            print(colored('[{datetime}] INIT DOGE @ {price:.5f}'.format(price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'blue'))
        if state['last_action'] == 'hold':
            print(colored('[{datetime}] HOLD DOGE @ {hold_at:.5f} | current price: {price:.5f}'.format(hold_at = state['last_price'], price=last_price, datetime=last_datetime.strftime("%Y-%m-%d %H:%M:%S")), 'yellow'))

sched = BlockingScheduler()

# Execute fn() at the start of each minute.
sched.add_job(process, trigger=CronTrigger(second=00))
sched.add_job(fetch_ochl, trigger=IntervalTrigger(seconds=5))

try:
    sched.start()
except (KeyboardInterrupt):
    sched.shutdown(wait=False)

def gracefully_exit(signum, frame):
    print('Stopping...')
    sched.shutdown()
