# this code executes ADF dickey fuller test to check if price action is a random walk
# it's described in succesfull algo trading book at 10.1.1
# candle = a+b*t + sum ( wi * candle_i)
# H0 -> all wi = 0 
# if H0 is rejected then price action is not ADF process, it's not a mean reverting regime 

import statsmodels.tsa.stattools as ts 
import datetime
import pandas_datareader.data as web
import matplotlib.pyplot as plt 
import pandas as pd

# plotting 
def plotme(x1,y1,x2=[],y2=[]): # plot one or two things 
    if len(x2)!=1:
        fig,ax=plt.subplots(2,1)
        ax[0].plot(x1,y1,'kx-')
        ax[1].plot(x2,y2,'rx-')
        ax[0].legend([y1.name])
        ax[1].legend([y2.name])     
        ax[0].grid(True)   
        ax[1].grid(True)
    else:
        fig,ax=plt.subplots(1,1)
        ax.plot(x1,y1,'rx-')
        ax.legend([y1.name])
        ax.grid(True)
        
    
    plt.show()




# 1. daily amazon stock price data - high, low, open,close,bolume, adj close 
start=datetime.datetime(2000,1,1)               # start if dataset 
end=datetime.datetime(2015,1,1)                 # end date of dataset 
ticker='AMZN'                                   # which stock 
src='yahoo'                                     # data source 

# 2. downloading data from web or reading from csv 
do_download =False 
if do_download:
    print('downloading data')
    df = web.DataReader(ticker, src, start,end)
    df.to_csv('adf.csv')
else:
    try:
        df=pd.read_csv('adf.csv')
    except FileNotFoundError as err:
        print('file not found bro')
        exit(1)


#plotme(df.index,df['Close'], df.index,df['Close'])

# 3. adf test 
H_zero=' wi=0 -> process is mean reverting '
lag=1
x=ts.adfuller(df['Close'], lag)
test_stat=x[0]
p_value=x[1]
lag=x[2]
n=x[3]
critical_values=x[4]

for k,v in critical_values.items():
    if test_stat > v:
        print(f'{test_stat} null hypothesis cannot be rejected with p-value {round(p_value,3)} with {k,v} interval whatever that means')
        print(' its unlikely process is  mean reverting :(  ')
    else:
        print(f' null hypothesis can be rejected with p-value {p_value} with {k} interval whatever that means')
        print(' its not unlikely process is mean reverting  :)  ')
        


