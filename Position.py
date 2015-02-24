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

class Position(list):
    #Position is a inherit class of list
    #the element of position is trading records
    #i.e. how many shares (first element) is sold/buy(the sign of first element)
    #at which price(second element)
    def __init__(self, sQ=1, trade=np.array([])):
        #sQ:whether it is stack (1) or queue (Otherwise)
        #trade:single trade record
        self.SQ=sQ
        if self.isTrade(trade) and trade!=np.array([]):
            self.addTrade(trade)

    def isTrade(self,trade):
        if type(trade)!=np.ndarray:
            return False
        if trade.size!=2:
            return False
        if type(trade[0])!=int and type(trade[0])!=float:
            return False
        if type(trade[1])!=int and type(trade[1])!=float:
            return False
        return True
    
    def addTrade(self,trade):
        #if trade is empty or there is no share to buy/sell
        if trade==np.array([]) or trade[0]==0:
            return 0
        #if self is an empty list
        if not self or trade[0]*self[0][0]>0:
            self.append(trade)
            return 0
        #if the portfolio is longing the stock but get a trade record to sell
        #or the portfolio is shorting the stock but get a trade record to buy
        firstTradeIndex=[0,-1][self.SQ==1]
        firstTrade=self[firstTradeIndex]
        #compare the first trade record to current trade record
        if abs(firstTrade[0])>abs(trade[0]):#if it is larger than current trade
            firstTrade[0]+=trade[0]
            return -trade[0]*(trade[1]-firstTrade[1])
        else:
            if self.SQ==1:#stack, FILO
                self.pop()
            else:#queue, FIFO
                self.popleft()
            trade[0]+=firstTrade[0]
            return firstTrade[0]*(trade[1]-firstTrade[1])+self.addTrade(trade)

    def clearPos(self):
        #clearing position
        #return total outstanding shares
        outstanding=0
        for i in range(0,len(self)):
            j=[len(self)-1-i,i][self.SQ==1]
            outstanding+=self[j][0]
            if self.SQ==1:
                self.pop()
            else:
                self.popleft()
        return outstanding

#get total outstanding share
    def totalShare(self):
        result=0
        for i in range(0,len(self)):
            result+=self[i][0]
        return result

    #check whether there is position
    def isempty(self):
        if len(self)==0:
            return True
        else:
            return False
