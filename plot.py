# import needed libraries
# import pandas as pd
# import matplotlib.pyplot as plt
# from pandas_datareader import data as web

import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np
from datetime import datetime

f = open("api.key", "r")
api_key = f.read()
f.close()


url='https://api.polygon.io/v1/historic/crypto/DOGE/USD/2021-02-04?limit=5000&apiKey={api_key}&offset=1612426331575'.format(api_key=api_key)
r = requests.get(url)
j = r.json()

for v in j['ticks']:
    v['date'] = datetime.fromtimestamp(v['t']/1000)

df = pd.DataFrame.from_dict(j['ticks'])

df.set_index('date', inplace=True)

df['MA20'] = df['p'].rolling(window=20).mean()
df['20dSTD'] = df['p'].rolling(window=20).std()
df['upper'] = df['MA20'] + (df['20dSTD'] * 2)
df['lower'] = df['MA20'] - (df['20dSTD'] * 2)

print (df)

plt.plot(df[['MA20', 'upper', 'lower']])
plt.axis('tight')
plt.ylabel('Price')
plt.show()

# Make function for calls to Yahoo Finance
def get_adj_close(ticker, start, end):
    '''
    A function that takes ticker symbols, starting period, ending period
    as arguments and returns with a Pandas DataFrame of the Adjusted Close Pricesimport numpy as np
    for the tickers from Yahoo Finance
    '''
    url='https://api.polygon.io/v1/historic/crypto/DOGE/USD/2021-02-04?limit=1000&apiKey={api_key}'
    r = requests.get(url)
    j = r.json()
    df = pd.DataFrame.from_dict(j['ticks'])


    # stockprices['MA20'] = stockprices['close'].rolling(window=20).mean()
    # stockprices['20dSTD'] = stockprices['close'].rolling(window=20).std()

    # stockprices['Upper'] = stockprices['MA20'] + (stockprices['20dSTD'] * 2)
    # stockprices['Lower'] = stockprices['MA20'] - (stockprices['20dSTD'] * 2)