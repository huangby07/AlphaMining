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


from Default import DEFAULT_YEAR
from Tools import elementExistInList, isTime

class Simulator:
    
    def __init__(self, strategy, marketRange,dateRange,simBegin,cash):
        self.strategy=strategy#the strategy handler should contain at least
        self.market=marketRange#the np.array specifies how many stocks are \
        #taken into consideration
        self.date=dateRange
        if simBegin>dateRange[1] or simBegin<dateRange[0]:
            print "Error in Simulator::__init__: simulation begin date exceeds \
date range"
            return
        self.begin=simBegin
        self.stock=gd.stockData(sN=marketRange,bD=dateRange[0],\
                             eD=dateRange[1])
        ####################pdb.set_trace()####################
        for iName in self.stock.stockName:
            if not self.stock.stockValid(iName):#if the data is not enough
                np.delete(self.market,np.where(self.market==iName))
                self.stock.delStock(iName)
        self.marketInfo=web.DataReader('^GSPC','yahoo',dateRange[0],\
                                       dateRange[1])
        self.marketDay=self.marketInfo.index.tolist()
        self.orders=dict()
        self.cash=cash

    def sim(self, end=None):
        
        if not isTime(end):
            end=self.date[1]
        #initialize account balance
        self.accountBalance=pd.Series(0,\
                                      index=self.marketInfo[self.begin:end].index)
        #initialize position
        self.position=dict.fromkeys(self.market)
        for iName in self.market:
            self.position[iName]=ps.Position()
        currentDay=self.begin-dt.timedelta(days=1)
        while currentDay<=end:
            currentDay+=dt.timedelta(days=1)
            #if current day is not market day
            #continue
            if elementExistInList(self.marketDay,currentDay)==False:
                continue
            #################################
            #####input data to strategy class#######
            #################################
            ###Then get the output trading strategy###
            ##################################
            trimStock=self.stock.deepCopy()
            trimStock.changeStockDate(newED=currentDay)
            self.strategy.update(currentDay, self.position,trimStock,\
                                 self.marketInfo[self.marketInfo.index<=currentDay],\
                                 self.cash)
            #type of order is a tuple
            self.orders[currentDay]=self.strategy.getStrategy(currentDay)
            self.cash+=self.calculatePos(currentDay)[0]
            self.accountBalance[currentDay]=self.cash+\
                                             self.calculateBalance(currentDay)
        #after the end of the day
        #clear all position to calculate total cash
        for iName in self.position.keys():
            finalPrice=self.stock.stockPrice(iName,currentDay)
            self.cash+=self.position[iName].clearPos()*finalPrice
        self.accountBalance[-1]=self.cash+self.calculateBalance(currentDay)

    def calculateBalance(self,day):
        totalB=0
        for iName in self.position:
            if self.position[iName]!=None and \
               self.position[iName].isempty()==False:
                share=self.position[iName].totalShare()
                price=self.stock.stockPrice(iName,day)
                totalB+=share*price
        return totalB

    def calculatePos(self, currentDay):
        #if there is no order information about current day
        #or if there is no order today
        if np.where(np.array(self.orders.keys())==currentDay)[0].size==0 or\
           self.orders[currentDay]==():
            return (0,0)
        totalReturn=0
        totalCashFlow=0
        for singleOrder in self.orders[currentDay]:
            tSymbol=singleOrder[0]
            try:
                tAction=singleOrder[1]
            except:
                ####################pdb.set_trace()####################
                pass
            tType=singleOrder[2]
            tPrice=singleOrder[3]
            tAmount=int(float(singleOrder[4]))
            if np.where(self.market==tSymbol)[0].size==0:
                continue
            #currently only support market order
            #invalid order
            if tAction!="buy" and tAction!="sell":
                continue
            if tAction=="buy":
                amount=tAmount
            else:
                amount=-tAmount
            marketPrice=self.stock.stockPrice(tSymbol,currentDay)
            newTrade=np.array([amount,marketPrice])
            totalReturn+=self.position[tSymbol].addTrade(newTrade)
            totalCashFlow+=-amount*marketPrice
        return (totalCashFlow,totalReturn)
        
        
    
