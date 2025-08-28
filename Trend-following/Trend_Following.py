#!/usr/bin/env python
# coding: utf-8

# In[20]:


#import data using ccxt for live data
import ccxt
import pandas as pd
#assign the exchange to be binance in this case
exchange = ccxt.binance()
#this lets us easily change the conditions for fetching data
symbol = "BTC/USDT"
timeframe = '1h'
limit = 500
#fetch the recent OHLCV candles
ohlcv = exchange.fetch_ohlcv(symbol, timeframe = timeframe , limit=limit)

#create a pandas data frame for easy data manipulation
df = pd.DataFrame(ohlcv, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#change the timestamp to a readable time
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#change timestamp column as the index of the dataframe
df.set_index('timestamp', inplace = True)#inplace modifies the df

print(df.head())

#next we calculate EMA- Exponential Moving Average
ema_period = 20 #short term 
df['EMA_20'] = df['close'].ewm(span=ema_period, adjust = False).mean()#using pd we can calutlate ema


#next we create a function to generate signals that takes df is input(trend - following logic)
def generate_signals(df):
    '''This function generates signals based on trend following logic.
    When price is above EMA we buy assuming the price follows the upward trend.
    When price is below EMA we sell assuming the price follows the downward trend.
    When there is no crossover, we hold.

    '''
    signals = [] #an empty list to store signals

    for i in range(len(df)):# this loops through the dataframe
        if i == 0 :
            signals.append('HOLD')#this deals with the first row as it has no previous value
        #generates buy signal
        elif df['close'].iloc[i] > df['EMA_20'].iloc[i] and df['close'].iloc[i-1] <= df['EMA_20'].iloc[i-1]:
            signals.append("BUY")
        #generates sell signal
        elif df['close'].iloc[i] < df['EMA_20'].iloc[i] and df['close'].iloc[i-1] >= df['EMA_20'].iloc[i-1]:
            signals.append("SELL")
        #hold if there is no crosover
        else:
            signals.append("HOLD")
    df['signal'] = signals #add signals to df



# In[21]:


generate_signals(df)
print(df[['close','EMA_20','signal']].tail(20))


# In[22]:


def backtest(df, starting_capital=1000):
    capital = starting_capital  # starting cash in USD
    position = 0  # BTC amount currently held

    for i in range(len(df)):
        price = df['close'].iloc[i]

        # BUY signal
        if df['signal'].iloc[i] == "BUY" and position == 0:
            position = capital / price  # buy BTC with all cash
            capital = 0

        # SELL signal
        elif df['signal'].iloc[i] == "SELL" and position > 0:
            capital = position * price  # sell all BTC for cash
            position = 0

    # If still holding BTC at the end, convert to cash
    if position > 0:
        capital = position * df['close'].iloc[-1]

    return capital


# In[23]:


final_capital = backtest(df, starting_capital=1000)
print("Final capital after backtest:", final_capital)


# In[24]:


import matplotlib.pyplot as plt
plt.figure(figsize=(14,7))
plt.plot(df['close'], label='BTC/USDT', color='blue')
plt.plot(df['EMA_20'], label='EMA 20', color='orange')

# Plot BUY signals
buy_signals = df[df['signal'] == 'BUY']
plt.scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', label='BUY', s=100)

# Plot SELL signals
sell_signals = df[df['signal'] == 'SELL']
plt.scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', label='SELL', s=100)

plt.title('BTC/USDT Price with EMA 20 and Buy/Sell Signals')
plt.xlabel('Time')
plt.ylabel('Price (USDT)')
plt.legend()
plt.grid(True)
plt.show()
plt.savefig("screenshot.png", dpi=300, bbox_inches='tight')

# In[ ]:




