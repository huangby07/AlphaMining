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
from Default import DEFAULT_YEAR, DEFAULT_CASH

from Tools import elementExistInList, isTime



class Strategy:
    def __init__(self,marketRange=np.array([]),marketInfo=pd.DataFrame(),\
                 cash=DEFAULT_CASH):
        self.marketRange=marketRange
        #self.stockInfo=
        self.marketInfo=marketInfo
        self.position=dict()
        self.cash=cash
        self.currentDay=dt.datetime(DEFAULT_YEAR,1,1)

    def update(self, currentDay=None,\
               position=dict(),stock=gd.stockData(np.array([""])),\
               marketInfo=pd.DataFrame(), cash=-1):
        if isTime(currentDay):
            self.currentDay=currentDay
        if position!=dict():
            #Delete empty entries
            for iSymbol in position.keys():
                if position[iSymbol]==None:
                    position.pop([iSymbol])
            self.position=position
        if stock!=gd.stockData(np.array([""])):
            self.stock=stock
        if marketInfo.empty!=True:
            self.marketInfo=marketInfo
        if cash!=-1:
            self.cash=cash

    def getStrategy(self,currentDay):
       # if self.validateDate(currentDay)==False:
           # print "Exception Strategy::Strategy::getStrategy: \
#Incomplete information!"
        #    return ("False")
        #this function should be overrided in inherit class
        return ()
    
    def validateDate(self,cDay):
        if elementExistInList(self.marketInfo.index,cDay)==False:
            return False
        stockInfo=self.stock.stockInfoGet(symbol="*")
        if len(stockInfo)==0:
            pdb.set_trace()#%
            return False
        noS=0
        for iName in stockInfo.keys():
            if elementExistInList(stockInfo[iName].index,cDay)==False:
                noS+=1
        if noS==len(stockInfo):
            pdb.set_trace()#%
            return False
        return True


