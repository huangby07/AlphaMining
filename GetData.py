#Reading stock data
#Example is shown at the bottom of this file
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

from Tools import *

from Default import DEFAULT_YEAR, Default_Price

import copy

class stockData:
    #if the new instance's required time span is within the available time span,
    #then the stockData class directly pull data from the existing files
    #otherwise it extend the existing file
    filePath='E:\\StockDatabase\\'
    dataSource='yahoo'
    beginDate=dt.datetime(2010,1,1)#start time
    endDate=dt.datetime.combine(dt.date.today(),dt.datetime.min.time())#end time, today
    NYSEFILE="NYSEF.csv"
    NASDAQFILE="NASDAQF.csv"
    ETFFILE="AllETFs.csv"
    STOCKPRICE=filePath+ "Prices\\"
    #DEFAULTSTOCK="^GPSC"
    LISTFILE="StockList.txt"
    DEFAULTMARKET="^GSPC"
    stockName=np.array([],dtype=np.dtype(str))
    stockInfo=dict()
    def __init__(self, sN=np.array([]), fP='E:\\StockDatabase\\',dS='',\
                 bD=None,eD=None,inputFileName=LISTFILE,webEnable=1):
        self.webEnable=webEnable
        ######################pdb.set_trace()######################
        if type(sN)==np.ndarray and sN!=np.array([]):
            ######################pdb.set_trace()######################
            self.stockName=sN
        else:
            try:
                ######################pdb.set_trace()######################
                sList=np.genfromtxt(self.filePath+inputFileName,dtype='str')
                self.stockName=sList
            except:
                ######################pdb.set_trace()######################
                print "stockData::__init__: Exception raises during attempting \
getting stock list!"
        if fP!='':
            self.filePath=fP
        if dS!='':
            self.dateSource=dS
        if isTime(bD):
            self.beginDate=bD
        if isTime(eD):
            ####################pdb.set_trace()####################
            self.endDate=eD
        self.stockNameUpdated=np.array([])
        self.marketInitialized=0
        #if user just wants an empty instance:
        if self.stockName.size==1 and self.stockName[0]=="":
            self.isempty=1
        else:
            self.isempty=0
            self.notEmptyInit()
        

#############################################################
#############################################################
#############################################################
    #interface to add new stocks to the class
    def addNewStock(self, newStockList):
        if self.isempty==1:
            self.notEmptyInit()
        for singleStockName in newStockList:
            ######################pdb.set_trace()######################
            if self.checkExist(singleStockName)==False:
                continue
            else:
                self.stockName=np.append(self.stockName,singleStockName)
        ######################pdb.set_trace()######################
        self.stockInfoUpdate(1)#update stock by skipping existing stock

    def delStock(self,symbol):
        #delete a stock from the database
        if symbol in self.stockName:
            np.delete(self.stockName,np.where(self.stockName==symbol))
        if symbol in self.stockInfo.keys():
            self.stockInfo.pop(symbol)

#generate a brand new instance from self
        #the copy.deepcopy only copies the data within 2-level depth
        #need to recursively call deepcopy if there is more depth
    def deepCopy(self):
        result=copy.deepcopy(self)
        #result.marketData=self.marketData.copy(deep=True)
        result.stockInfo=copy.deepcopy(self.stockInfo)
        for iName in result.stockInfo.keys():
            #result.stockInfoInsert(iName,pd.DataFrame())
            result.stockInfoInsert(iName,copy.deepcopy(self.stockInfoGet(iName)))
        return result

    def changeStockDate(self,newBD=None,\
                        newED=None):
        flagExpand=3#default:just trim the existing data(efficient)
        #see stockInfoUpdate
        oldbeginDate=self.beginDate
        oldendDate=self.endDate
        ####################pdb.set_trace()####################
        if isTime(newBD):
            ####################pdb.set_trace()####################
            self.beginDate=newBD
        if isTime(newED):
            ####################pdb.set_trace()####################
            self.endDate=newED
        self.marketInit()
        ####################pdb.set_trace()####################
        self.updateDates()
        ####################pdb.set_trace()####################
        if self.beginDate<oldbeginDate or self.endDate>oldendDate:
            flagExpand=2
        ####################pdb.set_trace()####################
        self.stockInfoUpdate(flagExpand)#update all existing stock

    #function related to read and write stock info
    def stockInfoGet(self,symbol="*",series="DataFrame", \
                     begin=None,\
                     end=None):
        #if symbol=="*", the function will return the whole stockInfo dictionary
        #at this time, the sereis does not work
        #only the beginDate and endDate works
        if symbol=="*":
            result=copy.deepcopy(self.stockInfo)
        else:
            try:
                result={symbol:copy.deepcopy(self.stockInfo[symbol])}
            except:
                pass
                 ####################pdb.set_trace()####################
        
        if isTime(begin) or isTime(end):
            if not isTime(begin):
                begin=self.beginDate
            if not isTime(end):
                end=self.endDate
            for singleStockName in result.keys():
                result[singleStockName]=result[singleStockName]\
                                         [result[singleStockName].index>=begin]
                result[singleStockName]=result[singleStockName]\
                                         [result[singleStockName].index<=end]
        try:
            if symbol=="*":
                return result
            if elementExistInList(result[symbol]["Source"].values,'google')\
               and series=='Close':
                print "Could not get actual close price from data set from google"
            if series=='DataFrame':
                return result[symbol]
            else:
                return result[symbol][series]
        except:
            print "Error in GetData::stockData::stockInfoGet. Please check the \
symbol or series is correct!"

    #return the actual price of the stock at currentDay
    def stockPrice(self,symbol,currentDay,unExisted=-1,Adj=1):
        #unExisted denotes whether the return value is restricted to be the price of
        #the exactly day or
        #-1: the last available price (if price of currentDay does not exist)
        #1: the next available price (if price of currentDay does not exist)
        if not self.stockValid(symbol):
            return Default_Price()
        close="Adj Close" if Adj==1 else "Close"
        try:
            return self.stockInfoGet(symbol,close,currentDay,currentDay)\
                   .values[0]
        except:
            if unExisted==0:
                print "GetData::stockData::stockPrice exception: check symbol \
and day"
            else:
                avaiDay=nearestDay(self.stockTradingDay(symbol),\
                                   currentDay,unExisted)
                return self.stockPrice(symbol,avaiDay,0,Adj)

    def stockTradingDay(self,symbol):
        if not self.stockValid(symbol):
            return None
        return self.stockInfoGet(symbol).index.tolist()

    def stockValid(self,symbol):
        #the symbol does not exist in market
        #the symbol is not in data base
        #the symbol's data is None
        if not self.checkExist(symbol):
            return False
        if not symbol in self.stockName:
            return False
        if not symbol in self.stockInfo.keys():
            return False
        if type(self.stockInfoGet(symbol))==type(None):
            return False
        if self.stockInfoGet(symbol).empty:
            return False
        return True
        
#############################################################
#############################################################
#############################################################

    def marketInit(self, begin=None, end=None):
        if not isTime(begin):
            begin=self.beginDate
        if not isTime(end):
            end=self.endDate
        if self.marketInitialized!=0 and \
           begin>=self.beginDate and end<=self.endDate:
            self.marketData=self.marketData[self.marketData.index<=end]
            self.marketData=self.marketData[self.marketData.index>=begin]
        else:
            self.marketData=self.readStockWeb(self.DEFAULTMARKET,\
                                              begin,end,enableOR=1)
        self.marketInitialized=1
    
    def notEmptyInit(self):
       #load NYSE and NASDAQ
        with open(self.filePath+self.NYSEFILE, 'r') as f:
            self.NYSE=pd.read_csv(f)
        with open(self.filePath+self.NASDAQFILE,'r') as f:
            self.NASDAQ=pd.read_csv(f)
        with open(self.filePath+self.ETFFILE,'r') as f:
            self.ETF=pd.read_csv(f)
       ######################pdb.set_trace()######################
        self.marketInit()
        ######################pdb.set_trace()######################
        self.updateDates()
        ######################pdb.set_trace()######################
        self.stockInfoUpdate(0)

    def updateValid(self):
        for iName in self.stockName:
            if not stockValid(iName):
                self.stock.delStock(iName)
        
    def updateDates(self):
        #update the beginDate and endDate to the nearest market day
        ######################pdb.set_trace()######################
        marketDay=np.array(self.marketData.index.tolist())
        try:
            self.beginDate=nearestDay(marketDay,self.beginDate,1)
        except:
            pdb.set_trace()#%
        self.endDate=nearestDay(marketDay,self.endDate,1)
        ######################pdb.set_trace()######################

    #sdef setBeginDate(self,begin):
    
    def stockInfoInsert(self, symbol, newStock, source='yahoo'):
        #directly insert the datasource to each row
        ######################pdb.set_trace()######################
        if elementExistInList(newStock.columns.values,"Source")==False:
            newColumn=pd.Series(source,index=newStock.index)
            newStock["Source"]=newColumn
        self.stockInfo[symbol]=newStock

    
        #initialize/update the stockInfo
    def stockInfoUpdate(self, init=0):
        #init:
        #0: initialize
        #1:just update stock symbol(insert new stock)
        #2: update existing stock(ALL)
        #3: only trim current data(more efficient)
        if init==2:
            self.stockNameUpdated=np.array([])
        if init==3:#do not need to read from web or from file
            for singleStockName in self.stockName:
                if not elementExistInList(self.stockInfo.keys(),singleStockName):
                    continue
                self.stockInfoInsert(singleStockName,\
                                                  self.stockInfoGet(singleStockName,\
                                                                    "DataFrame",self.beginDate,\
                                                                    self.endDate))
            return
        for singleStockName in self.stockName:
            #it is possible that the singleStockName is not listed in either market
            if self.checkExist(singleStockName)==False:
                continue#Here we should throw an exception
            if init==1:#not initialization, update just the stock
                ######################pdb.set_trace()######################
                if elementExistInList(self.stockNameUpdated,singleStockName):
                    continue
            fileName=self.STOCKPRICE + singleStockName + '.csv'
            if  os.path.isfile(fileName)==False:#if the data does not exist
                
                tempStock=self.readStockWeb(singleStockName)
                                             #web.DataReader(singleStockName,'yahoo',\
                                                                #self.beginDate,self.endDate)
                ####################pdb.set_trace()####################
                if type(tempStock)==int:#Read fail
                    continue
                tempStock=self.stockExpand(tempStock,singleStockName)[1]
                ####################pdb.set_trace()####################
                self.stockInfoInsert(singleStockName,tempStock)
                with open(fileName,'w') as f:
                    self.stockInfoGet(singleStockName).to_csv(f)
            else:#if the data exists, then test whether the time span is enough
                #flag=0#whether need to read from web
                #read file
                stock=self.readStockFile(fileName)
                flag, stock=self.stockExpand(stock,singleStockName)
                ######################pdb.set_trace()######################
                self.stockInfoInsert(singleStockName,stock)
                #if there is change, write the data back to file
                if flag==1:
                    with open(fileName,'w') as f:
                        self.stockInfoGet(singleStockName).to_csv(f)
    #expand the current temporary stock data to the time span within\
                        #[self.beginDate,self.endDate]
            #update stock list of updated stock
            self.stockNameUpdated=np.append(self.stockNameUpdated,\
                      singleStockName)

    def readStockFile(self,fileName,begin=None,end=None):
        if not isTime(begin):
            begin=self.beginDate
        if not isTime(end):
            end=self.endDate
        with open(fileName,'r') as f:
            stock=pd.read_csv(f,index_col=0,parse_dates=True)
        stock=stock[stock.index>=begin]
        stock=stock[stock.index<=end]
        return stock

                        
    def stockExpand(self,stock,singleStockName):
        dateRange=getDateRange(stock)
        stockBegin=dateRange[0]
        stockEnd=dateRange[1]
        ####################pdb.set_trace()####################
        flag=0#return whether there is expand
        if stockBegin>self.beginDate:#if the start date is less than required date
            flag=1
            getDataEndDate=stockBegin-dt.timedelta(days=1)
            #the end date is one day before existing data's startdate
            beforeStock=self.readStockWeb(singleStockName, \
                                          end=getDataEndDate)
            #web.DataReader(singleStockName,self.dataSource,\
            #self.beginDate,getDataEndDate)
            ####################pdb.set_trace()####################
            if type(beforeStock)!=int:
                stock=pd.concat([beforeStock,stock])
        if stockEnd<self.endDate:
            flag=1
            getDataBeginDate=stockEnd+dt.timedelta(days=1)
            afterStock=self.readStockWeb(singleStockName, \
                                                 begin=getDataBeginDate)
                    #web.DataReader(singleStockName,self.dataSource,\
                      #                        getDataBeginDate,self.endDate)
            ####################pdb.set_trace()####################
            if type(afterStock)!=int:
                stock=pd.concat([stock,afterStock])
        
        return (flag, stock)

#check whether the stock symbol is listed/valid
    def checkExist(self, symbol=""):
        if symbol=="":
            return False
        testNYSE=elementExistInList(self.NYSE["Symbol"],symbol)
        testNASDAQ=elementExistInList(self.NASDAQ["Symbol"],symbol)
        testETF=elementExistInList(self.ETF["Symbol"],symbol)
        if testNYSE==False and testNASDAQ==False and \
           testETF==False:
            return False
        else:
            return True

    #return the date range of available data of a given symbol
        #This is useless
        
    def getStockDate(self,symbol=""):
        if self.checkExist(symbol)==False:
            return None
        timeSeries=self.stockInfoGet(symbol,"Close").index.tolist()
        start=timeSeries[0]
        end=timeSeries[-1]
        result=np.array([start,end])
        return result

    def readStockWeb(self,symbol, begin=None, end=None,\
                     source=dataSource,enableOR=0):#priority is set to yahoo finance
        if self.webEnable+enableOR==0:
            return 0
        if not isTime(begin):
            begin=self.beginDate
        if not isTime(end):
            ####################pdb.set_trace()####################
            end=self.endDate
        def addAdj(stockR,source):
            if source=='yahoo':
                return stockR
            else:
                newSeries=pd.Series(stockR["Close"],index=stockR.index)
                stockR["Adj Close"]=newSeries
                return stockR
        try:
            ####################pdb.set_trace()####################
            stock=web.DataReader(symbol,source,begin,end)
            sColumn=pd.Series(source,index=stock.index)
            stock["Source"]=sColumn
            stock=addAdj(stock,source)
            ######################pdb.set_trace()######################
            return stock
        except:
            print "stockData::readStockWeb exception: possible HTTP 404 error \
from pandas lib. Symbol:" + symbol + " from data source " + source
            ######################pdb.set_trace()######################
            if source=='yahoo':
                source='google'
            else:
                source='yahoo'
            print "Now trying to retrieve data from " + source +"."
            try:
                stock=web.DataReader(symbol,source,begin,end)
                sColumn=pd.Series(source,index=stock.index)
                stock["Source"]=sColumn
                stock=addAdj(stock,source)
                return stock
            except:
                print "Both data source could not retrieve data. Check \
internet connection!"
                return 0

        



    




        
if __name__=="__main__":
    #stockList=np.genfromtxt(
    StockInitial=stockData(np.array([""]))#np.array(["GOOG"])
    StockInitial.addNewStock(np.array(["AAPL"]))
