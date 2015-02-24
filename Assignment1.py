#Computational investing homework 1
#Run command in IPython
#%run C:\Users\B\Dropbox\Code\CII\Assignment1.py


import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#load data from yahoo using DataReader
import pandas.io.data as web

#optimization tool
import scipy.optimize as opt

import math#import the math lib


TOTALMONEY=100000 #total amount of money, $100,000
dateBegin=dt.datetime(2013,1,1)
dateEnd=dt.datetime(2013,12,31)

stockName=np.array(["TSLA","AAPL","GILD","F"])

#the dictionary storing stock's prices, etc.
stockInfo=dict.fromkeys(stockName)
#adjusted price of stocks
adjPrice=dict.fromkeys(stockName)
actualPrice=np.zeros(stockName.size)

for singleStockName in stockName:
    stockInfo[singleStockName]=web.DataReader(singleStockName,'yahoo',\
                                              dateBegin,dateEnd)
    #get the values of TimeSeries
    adjPrice[singleStockName]=stockInfo[singleStockName]["Adj Close"].values
    index=np.where(singleStockName==stockName)[0][0]
    actualPrice[index]=stockInfo[singleStockName]["Close"].values[0]

#web.DataReader('^GSPC','yahoo')  # S&P 500
#web.DataReader('^IXIC','yahoo')  # NASDAQ

market=web.DataReader("^GSPC",'yahoo',dateBegin,dateEnd)
marketAdj=market["Adj Close"].values

#generate the list of time
time=stockInfo[stockName[0]]["Adj Close"].index.tolist()


##############################################################
#optimizing the portfolio by total return
def totalReturn(amount):
#using marketAdj, adjPrice
#amount is a numpy array indicating the amount of each stock
    
    stockReturn=dict.fromkeys(stockName)
    totalReturn=0
    for iName in stockName:
        i=np.where(stockName==iName)[0][0]
        lastElement=adjPrice[iName].size-1
        stockReturn[iName]=adjPrice[iName][lastElement]-adjPrice[iName][0]
        totalReturn+=stockReturn[iName]*amount[i]

    return -totalReturn#need to minimize negative value of total return in order
#to maximize total Return

#optimizing the portfolio by sharpe ratio
def sharpeRatio(amount):
    stockDailyReturn=dict.fromkeys(stockName)
    totalDailyReturn=np.zeros(adjPrice[stockName[0]].size-1)
    for iName in stockName:
        i=np.where(stockName==iName)[0][0]
        stockDailyReturn[iName]=\
                                  adjPrice[iName][1:]-adjPrice[iName][:-1]
        totalDailyReturn+=stockDailyReturn[iName]*amount[i]
    sharpe=math.sqrt(totalDailyReturn.size)*np.average(totalDailyReturn)\
            /np.std(totalDailyReturn)
    return -sharpe #maximizing sharpe ratio means minimize minus sharpe ratio

#derivative
def totalReturn_deriv(weight):
    result=np.array([])
    for iName in stockName:
        lastElement=adjPrice[iName].size-1
        priceReturn=adjPrice[iName][lastElement]-adjPrice[iName][0]
        result=np.concatenate([result,np.array([priceReturn])])
    return -result#the derivative should be negative because it is minimizing\
#the negative total return
    
##############################################################

cons=({ "type":"ineq",\
                "fun":      lambda x: np.array([-(x*actualPrice).sum()\
                                                +TOTALMONEY]),
                "jac":      lambda x: -actualPrice},
           {    "type":     "ineq",\
                "fun":      lambda x: x})

#res=opt.minimize(totalReturn, [0,0,0,600],jac=totalReturn_deriv,\
                 #constraints=cons,method="SLSQP",options={"disp": True})

res=opt.minimize(sharpeRatio, [0,0,0,600],\
                 constraints=cons,method="SLSQP",options={"disp": True})

print (res.x)

#output
portfolioAdj=np.zeros(adjPrice[stockName[0]].size)
for iName in stockName:
    i=np.where(iName==stockName)[0][0]
    portfolioAdj+=adjPrice[iName]*res.x[i]

portfolioAdj/=portfolioAdj[0]
marketAdj/=marketAdj[0]
outputY=np.array([portfolioAdj,marketAdj]).T#Notice that the plot is a seeking
#column as different dataset and row as time series
#e.g.
#       F   AAPL
#       13  700
#       14  701
#       ...     ...
plt.clf()
plt.plot(time,outputY)
plt.legend(["Portfolio","SP500"])
plt.ylabel("Adjusted return")
plt.xlabel("Date")
plt.savefig("result.pdf",format="pdf")









