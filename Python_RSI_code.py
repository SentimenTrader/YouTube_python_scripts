#!/usr/bin/env python
# coding: utf-8

# <div align = "center">
# <h1>Trading Algorithm using RSI</h1>
# </div>

# <h3>RSI: Relative Strength Index</h3>
# 
# Momentum indicator\
# Range Bound (between 0 and 100)\
# Overbought or Oversold
# 
# <h3>Formula:</h3>
# 
# Initial RSI: 100- (100/(1+(avg up move/avg down move)))
# 
# RSI: 100- (100/(1+((previous average up x 13 + current up move)/(previous average down move x 13 + current down move)))
# 
# 
# <div align = 'center'>
#     <h3>Stock: Apple (AAPL)</h3>
#    <img src="attachment:Screen%20Shot%202020-11-15%20at%2012.59.56%20AM.png" width="600" align = "center"/>
# </div>
# 
# <h3>Algorithm Rules</h3>
# 
# 1) Buy Apple stock when RSI reaches 40 or below\
# 2) Sell when it's RSI exceeds 70

# In[1]:


##import all necessary libraries
#pip install *insert library name*

import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import datetime as dt 
import matplotlib.pyplot as plt


# In[2]:


##Get stock price data
ticker = 'AAPL'

#Data time period
now = dt.datetime.now()
startyear = 2017
startmonth=1
startday=1
start = dt.datetime(startyear, startmonth, startday)

#get data from YFinance
df = pdr.get_data_yahoo(ticker, start, now)

df


# In[5]:


##Calculate 14 day RSI
#create the columns we need to calculate 14 day RSI
df['Up Move'] = np.nan
df['Down Move'] = np.nan
df['Average Up'] = np.nan
df['Average Down'] = np.nan
df['RS'] = np.nan
df['RSI'] = np.nan

#Calculate Up Move & Down Move
for x in range(1, len(df)):
    df['Up Move'][x] = 0
    df['Down Move'][x] = 0
    
    if df['Adj Close'][x] > df['Adj Close'][x-1]:
        df['Up Move'][x] = df['Adj Close'][x] - df['Adj Close'][x-1]
        
    if df['Adj Close'][x] < df['Adj Close'][x-1]:
        df['Down Move'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x-1])  
        
#Calculate initial Average Up & Down, RS and RSI
df['Average Up'][14] = df['Up Move'][1:15].mean()
df['Average Down'][14] = df['Down Move'][1:15].mean()
df['RS'][14] = df['Average Up'][14] / df['Average Down'][14]
df['RSI'][14] = 100 - (100/(1+df['RS'][14]))

#Calculate rest of Average Up, Average Down, RS, RSI
for x in range(15, len(df)):
    df['Average Up'][x] = (df['Average Up'][x-1]*13+df['Up Move'][x])/14
    df['Average Down'][x] = (df['Average Down'][x-1]*13+df['Down Move'][x])/14
    df['RS'][x] = df['Average Up'][x] / df['Average Down'][x]
    df['RSI'][x] = 100 - (100/(1+df['RS'][x]))
    
print(df)


# In[6]:


#Chart the stock price and RSI
plt.style.use('classic')
fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
fig.suptitle('Stock Price (top) & 14 day RSI (bottom)')
axs[0].plot(df['Adj Close'])
axs[1].plot(df['RSI'])
axs[0].grid()
axs[1].grid()


# In[7]:


##Calculate the buy & sell signals
#initialize the columns that we need
df['Long Tomorrow'] = np.nan
df['Buy Signal'] = np.nan
df['Sell Signal'] = np.nan
df['Buy RSI'] = np.nan
df['Sell RSI'] = np.nan
df['Strategy'] = np.nan

#Calculate the buy & sell signals
for x in range(15, len(df)):
    
    #calculate "Long Tomorrow" column
    if ((df['RSI'][x] <= 40) & (df['RSI'][x-1]>40) ):
        df['Long Tomorrow'][x] = True
    elif ((df['Long Tomorrow'][x-1] == True) & (df['RSI'][x] <= 70)):
        df['Long Tomorrow'][x] = True
    else:
        df['Long Tomorrow'][x] = False
        
    #calculate "Buy Signal" column
    if ((df['Long Tomorrow'][x] == True) & (df['Long Tomorrow'][x-1] == False)):
        df['Buy Signal'][x] = df['Adj Close'][x]
        df['Buy RSI'][x] = df['RSI'][x]
        
    #calculate "Sell Signal" column
    if ((df['Long Tomorrow'][x] == False) & (df['Long Tomorrow'][x-1] == True)):
        df['Sell Signal'][x] = df['Adj Close'][x]
        df['Sell RSI'][x] = df['RSI'][x]
        
#calculate strategy performance
df['Strategy'][15] = df['Adj Close'][15]

for x in range(16, len(df)):
    if df['Long Tomorrow'][x-1] == True:
        df['Strategy'][x] = df['Strategy'][x-1]* (df['Adj Close'][x] / df['Adj Close'][x-1])
    else:
        df['Strategy'][x] = df['Strategy'][x-1]
        
print(df)


# In[8]:


##Chart the buy/sell signals 
plt.style.use('classic')
fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
fig.suptitle('Stock Price (top) & 14 day RSI (bottom)')

#chart the stock close price & buy/sell signals
axs[0].scatter(df.index, df['Buy Signal'],  color = 'green',  marker = '^', alpha = 1)
axs[0].scatter(df.index, df['Sell Signal'],  color = 'red',  marker = 'v', alpha = 1)
axs[0].plot(df['Adj Close'], alpha = 0.8)
axs[0].grid()

#chart RSI & buy/sell signals
axs[1].scatter(df.index, df['Buy RSI'],  color = 'green', marker = '^', alpha = 1)
axs[1].scatter(df.index, df['Sell RSI'],  color = 'red', marker = 'v', alpha = 1)
axs[1].plot(df['RSI'], alpha = 0.8)
axs[1].grid()


# In[9]:


##some performance statistics
#calculate the number of trades
trade_count = df['Buy Signal'].count()

#calculate the average profit per trade
average_profit = ((df['Strategy'][-1] / df['Strategy'][15])**(1/trade_count))-1

#calculate the average # of days per trade
total_days = df['Long Tomorrow'].count()
average_days = int(total_days / trade_count)

print('This strategy yielded ', trade_count, ' trades')
print('The average trade lasted ', average_days, ' days per trade')
print('The average profit per trade was ', average_profit*100, '%')


# In[ ]:




