from __future__ import division
#Reading all stock information from yahoo finance
import datetime as dt
import pandas as pd
import numpy as np

#load data from yahoo using DataReader
import pandas.io.data as web

#check file existing
import os.path

#debugger
import pdb

#import stockData file
import GetData as gd
import Position as ps
from Strategy import *
from Default import DEFAULT_YEAR, DEFAULT_CASH, DEFAULT_SYMBOL_L
import Simulator as sm
from Tools import nearestDay, plotSeries


DEFAULT_NOS=5
#DEFAULT_RETURN=1

class sbStrategy(Strategy):
    def __init__(self,marketRange=np.array([]),marketInfo=pd.DataFrame(),\
                 cash=DEFAULT_CASH, nos=DEFAULT_NOS):
        Strategy.__init__(self,marketRange,marketInfo,cash)
        self.noS=nos

    def getStrategy(self,currentDay):
        ####################pdb.set_trace()####################
        if len(Strategy.getStrategy(self,currentDay))!=0:
            ####################pdb.set_trace()####################
            return ("False")
        tradingDay=np.array(self.marketInfo.index.tolist())
        year=currentDay.year
        #if current date is the first trading day of the year
        finalOrder=()
        if currentDay==nearestDay(tradingDay,dt.datetime(year,1,1)):
            finalOrder+=self.clearPosition()
        elif currentDay==nearestDay(tradingDay,\
                                    nearestDay(tradingDay,dt.datetime(year,1,1))+\
                                    dt.timedelta(days=1)):
            ####################pdb.set_trace()####################
            stockList=self.getWorst()
            for iName in stockList:
                
                shareP=self.stock.stockPrice(iName,currentDay)
                amount=int(self.cash/self.noS/shareP)
                finalOrder+=(np.array([iName,'buy','market','shareP',amount]),)
        return finalOrder

    def clearPosition(self):
        cpOrder=()
        for iSymbol in self.position.keys():
            #position is a dictionary from stock symbol to class Position
            #class Position is a inherit class of list
            totalShare=self.position[iSymbol].totalShare()
            cpOrder+=(np.array([iSymbol,'sell','market','0',totalShare]),)
        return cpOrder

    def getWorst(self):
        if self.currentDay<self.stock.beginDate+dt.timedelta(days=365):
            startDate=self.stock.beginDate
        else:
            startDate=self.currentDay-dt.timedelta(days=365)
        worstName=np.empty([1,self.noS],\
                           dtype='|S'+ str(DEFAULT_SYMBOL_L))[0]
        worstReturn=np.ones([1,self.noS])[0]
        for singleStockName in self.stock.stockInfo.keys():
            if not self.stock.stockValid(singleStockName):
                #it is possible that the stock is not listed
                #because in backtesting it is not yet IPOed
                continue
            #actual stock trading date, varies according to different stock
            stockDate=self.stock.stockTradingDay(singleStockName)
            #if the stock data is not in the range of current date
            #[startDate,self.currentDay]
            try:
                if stockDate[-1]<startDate or stockDate[0]>self.currentDay:
                    continue
            except:
                pdb.set_trace()#%
            #actual start date
            actualSD=nearestDay(stockDate,startDate)
            
            #actual end date
            actualED=nearestDay(stockDate,self.currentDay,-1)
            #price at the start of time period
            priceS=self.stock.stockInfoGet(singleStockName,"Adj Close",actualSD,\
                                           actualSD).values
            #price at the end of time period
            priceE=self.stock.stockInfoGet(singleStockName,"Adj Close",actualED,\
                                           actualED).values
            #stock return
            sR=(priceE-priceS)/priceS
            ####################pdb.set_trace()####################
            if sR<worstReturn[0]:
                worstReturn[0]=sR
                worstName[0]=singleStockName
                ####################pdb.set_trace()####################
                for i in range(1,self.noS):
                    if worstReturn[i-1]<worstReturn[i]:
                        worstReturn[i],worstReturn[i-1]=\
                                                          worstReturn[i-1],worstReturn[i]
                        worstName[i],worstName[i-1]=\
                                                      worstName[i-1],worstName[i]
            #####end sR<worstReturn[0]
        ###end for singleStockName in allStock.keys():
        return worstName


if __name__=="__main__":
    
    marketRange=\
                 np.genfromtxt(r"E:\StockDatabase\SP500.txt",dtype='str')
    begin=dt.datetime(2000,1,1)
    end=dt.datetime(2014,12,1)
    #print "Haha"
    marketInfo=web.DataReader("^GSPC",'yahoo',begin,end)
    #print "Haha"
    #stock=gd.stockData(sN=marketRange,bD=begin,eD=end)
    test=sbStrategy(marketRange,marketInfo)
    #test.update(end,stock=stock,cash=1000000)
    tradingDay=np.array(test.marketInfo.index.tolist())
    #actualEnd=nearestDay(tradingDay,\
                                   # nearestDay(tradingDay,dt.datetime(2011,1,1))+\
                                    #dt.timedelta(days=1))
    #test.getStrategy(actualEnd)
    dateRng=[nearestDay(tradingDay,begin),\
             nearestDay(tradingDay,end)]
    testp=sm.Simulator(test,marketRange,dateRng,\
                   nearestDay(tradingDay,dt.datetime(2001,1,1)),1000000)
    ####################pdb.set_trace()####################
    testp.sim()
    MarketData=testp.marketInfo[testp.begin:testp.date[-1]]["Adj Close"]
    plotSeries((testp.accountBalance,MarketData),\
                     sName=["Sb Strategy", r"S&P 500"],\
                     fileName=r"ResultFromSP500(1).pdf")




    
