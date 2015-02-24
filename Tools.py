#Reading all stock information from yahoo finance
import datetime as dt
import pandas as pd
import numpy as np

#load data from yahoo using DataReader
import pandas.io.data as web

#check file existing
import os.path

#plot figure
import matplotlib.pyplot as plt

#debugger
import pdb

def elementExistInList(listA,elementB):
    try:
        if type(listA)==pd.tseries.index.DatetimeIndex:
            listA=listA.tolist()
        if type(listA)!=np.ndarray:
            listA=np.array(listA)
    except:
        print "Exception in Strategy::elementExistInList: Could not convert listA\
to numpy.ndarray. Check the type of your input!"
        return False
    if np.where(listA==elementB)[0].size>0:
        return True
    else:
        return False


def nearestDay(dayList,day,offset=1):
    #return the day in dayList that is the nearest to the day
    #offset==1 means find next
    #offset==0 means no direction
    #offset==-1 means find before
    #the code below is only compatible with numpy.array
    #thus for data type list, we should first convert it to numpy.array
    if type(dayList)==list:
        dayList=np.array(dayList)
    if offset!=1 and offset!=-1 and offset!=0:
    ######################pdb.set_trace()######################
        offest=1
    if dayList.size==1:
    ######################pdb.set_trace()######################
        return dayList[0]
    if np.where(dayList==day)[0].size!=0:
    ######################pdb.set_trace()######################
    #the day appears in dayList
        return day
    if day<dayList[0]:
    ######################pdb.set_trace()######################
        return dayList[0]
    if day>dayList[-1]:
    ######################pdb.set_trace()######################
        return dayList[-1]
    iL=0
    iR=dayList.size-1
    ####################pdb.set_trace()####################
    while iR-iL!=1:
        i=(iR+iL)/2
        resultL=dayList[i]
        resultR=dayList[i+1]
        if day>resultL and day<resultR:
            if offset==1:
                return resultR
            if offset==-1:
                return resultL
            if offset==0:
                if day-resultL<resultR-day:
                    return resultL
                else:
                    return resultR
        ####################pdb.set_trace()######################
        if resultR<day:
            iL=i+1
        if resultL>day:
            iR=i
    ######################pdb.set_trace()######################
    if offset==1:
        return dayList[iR]
    if offset==-1:
        return dayList[iL]
    if offset==0:
        if day-dayList[iL]<dayList[iR]-day:
            return dayList[iL]
        else:
            return dayList[iR]

#given a dataframe get the date range of the dataframe
def getDateRange(dt=None):
#input argument dt is a dataframe
    #if dt==None:
       # return dt
    firstColumn=dt.columns.values[1]
    time=dt[firstColumn].index.tolist()
    begin=time[0]
    end=time[-1]
    result=np.array([begin,end])
    
    return result

def isTime(time=None):
    if type(time)!=dt.datetime and type(time)!=pd.tslib.Timestamp:
        return False
    return True

def plotSeries(inputSeries,xAxis=None,sName=None,xName=None,\
               yName=None, normalize=1, fileName="Result.pdf"):
    #inputSeries is a tuple or list that contains a group number of data
    #if xAxis==None, then try to find xAxis in one of the inputSeries
    #there are several input series types:
    #numpy.ndarray: do nothing
    #pd.Series: extract values and index(if xAxis==None and the index is longest)
    yAxis=np.array([])
    #assmeble the output data
    for ss in inputSeries:
        test=0
        if type(ss)==np.ndarray:
            test=1
            #print "ndarray"
            if len(ss.shape)>2:
                continue
            if len(ss.shape)==1:
                ss=np.array([ss])
            if len(ss.shape)!=1 and ss.shape[0]!=1:
                sResult=ss.T
            else:
                sResult=ss
        if type(ss)==pd.core.series.Series:
            test=1
            if type(xAxis)==type(None):
                xAxis=ss.index
            #print "Series"
            sResult=np.array([ss.values])
        if test==1:
            if normalize==1:
                sResult/=sResult[0]#normalize the data series to \
                #get a common start point 1
            if len(yAxis.shape)==1 and yAxis.size!=0:
                yAxis=np.array([yAxis])
            if yAxis.size==0:
                yAxis=sResult
            else:
                yAxis=np.concatenate((yAxis,sResult),axis=0)
    if type(xAxis)==None:
        print "Exception in Tools::plotSereis: No x axis!"
        return
    if len(yAxis.shape)==1 and yAxis.size!=0:
        yAxis=np.array([yAxis])
    fileType=fileName.split('.')[-1]
    plt.clf()
    plt.plot(xAxis,yAxis.T)
    plt.legend(sName)
    plt.ylabel(yName)
    plt.xlabel(xName)
    plt.savefig(fileName,format=fileType)
        


if __name__=="__main__":
    pass
    #plotSeries((marketData,testp.accountBalance),\
               #sName=["Portfolio","SP500"],fileName="Result.pdf")

