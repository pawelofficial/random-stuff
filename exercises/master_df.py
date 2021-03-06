# to do RSI, MACD, boeillinger bands 

# this code defines master df which i shall use as a dataset for ai stuff 
import pandas as pd 
import scipy.special
from scipy import stats
from scipy import integrate
import numpy as np 
from types import FunctionType
import matplotlib.pyplot as plt
import datetime
class masterdf:
    def __init__(self,csv_file:str = 'BTC-USD2022-06-04_2022-06-05.csv'):
        self.raw_df=pd.read_csv(csv_file,lineterminator=';') # read csv to df 
        self.df=pd.DataFrame() # master df 
        self.tformat='%Y-%m-%dT%H:%M:%S.%fZ'
        self.bcols=['open','close','low','high']
        
        # 1.0 normalizing functions 
        self.lambda_d={} # dictionary with lambda functions
        self.lambda_d['norm_max']= lambda ser: ser/ser.max() # normalizes with max 
        self.lambda_d['norm_avg']= lambda ser: ser/ser.avg() # normalized with ave 
        self.lambda_d['avg']= lambda ser: ser.avg()
        # 1.1 normalizing roll functions  
        self.lambda_d['norm_roll_max']=lambda ser,window: ser/(ser.rolling(window=window).max()) 
        #self.lambda_d['norm_roll_mean']=lambda ser,window: ser/(ser.rolling(window=window).mean()   )# normalization on rolling is the best 
        self.lambda_d['norm_roll_mean']=lambda ser,window: (ser -ser.rolling(window=window).min() )/(ser.rolling(window=window).max() -ser.rolling(window=window).min()  )
            # gotta work on above roll mean because it hits floor and ceiling because of max min, lets use z score from now on 
            # z score makes sense on rvs not on close,
            # below is z score
        self.lambda_d['norm_roll_mean']=lambda ser,window: (ser -ser.rolling(window=window).mean() )/(ser.rolling(window=window).std())
        self.lambda_d['roll_zscore']=lambda ser,window: (ser -ser.rolling(window=window).mean() )/(ser.rolling(window=window).std())
            
        
        # 2.0 roll functions 
        self.lambda_d['roll_std']=lambda ser,window: ser.rolling(window=window).std()
        # 2.1 ewm functions 
        self.lambda_d['ewm_mean']=lambda ser,window: ser.ewm(span=window).mean()
        # idk - integral 
        self.lambda_d['trapz'] = lambda ser,window: ser.rolling(window=window).apply(lambda x:np.trapz(x))

        # floors datetime series into a scale 
        self.lambda_d['floor_dt'] = lambda ser,scale: ser.apply(
                lambda dt : dt - datetime.timedelta(
                    minutes=(dt.minute) % scale,
                    seconds=dt.second,
                    microseconds=dt.microsecond)
                                                                )

        self.lambda_d['max'] = lambda df,key,tscale: df[[key,tscale]].groupby([tscale]).max().reset_index()
        
        # 3.0 row functions  
        self.lambda_d['convert_dt']= lambda x: datetime.datetime.strptime(x,self.tformat) # converts string to datetime  
        self.lambda_d['timestamp_to_day']=lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0)
        self.lambda_d['compute_sod']= lambda x: (self.lambda_d['convert_dt'](x) - self.lambda_d['convert_dt'](x).replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() # second of a day 




        
        self.row_functions=['convert_dt','compute_sod']
        
    def compute_lambda(self,func:str,ser:pd.Series,**kwargs): # leaving func and ser outside kwargs for readability
        # applies lambda fun to series and returns it 
        # if lambda requires more than one parameter it must be passed in kwargs in correct order
        # if order, based on naming is incorrect error is raised 
        lambda_arguments=self.lambda_d[func].__code__.co_varnames[1:] # lambda keys except 1st which is ser
        kwargs_keys=tuple(k for k,v in kwargs.items()) # kwargs keys 
        if  lambda_arguments!=kwargs_keys:
            print('!!! incorrect lambda function order or naming !!!')
            print(f'lambda arguments: {lambda_arguments}')
            print(f'kwargs_keys: {kwargs_keys} \n\n' )
            raise()
        t=tuple(v for k,v in kwargs.items())          # kwargs values
        
        if func in self.row_functions: # row functions need different syntax 
            return ser.apply(self.lambda_d[func] )
         
        return self.lambda_d[func](*tuple((ser,)+t) ) # not sure if this approach makes sense tbg 
    
    def replace_na(self,ser: pd.Series, value: float = 0,inplace: bool =True): # replaces NaN in series to value 
        if inplace:
            ser.fillna(value=value,inplace=inplace) # love one liners
            return 
        return ser.fillna(value=value,inplace=False)
    
    def aggregate(self, cols: list = ['open','close','low','high','volume'], tscale: int =5  ): 
        # returns dataframe with aggregate values from self.df, self.df must contain
        # aka 5min candle at time 09:05 contains data from <09:05 -> 09:09>
        if len ( list ( set(cols).intersection( list(self.df.columns) ) )  ) !=len(cols): # check if all your cols exist in df 
            print('incorrect columns specified ')
            print(f'your cols : {cols}')
            print(f'df cols: {list(self.df.columns)}')
            raise 
        if 'timestamp' not in (self.df.columns): # check if timestamp exists in df 
            print(' timestamp column  must exist in df ')
            raise
        
        dt_col='dt_'+str(tscale) # name of datetime column used for aggregation  

        
        if 'dt' not in list(self.df.columns): # make a datetime column if it doesn't exist in self.df 
            self.df['dt']=self.compute_lambda(func='convert_dt',ser=raw_df['timestamp'])  # making datetime column in self df 
        if dt_col not in list(self.df.columns): # make an aggregate dt column in self.df if it doesn't exist 
            self.df[dt_col]=self.compute_lambda(func='floor_dt',ser=self.df['dt'],scale = tscale ) 
        # declare dataframeto be returned 
        agg_df=pd.DataFrame()
        agg_df[dt_col] = self.compute_lambda(func='floor_dt',ser=self.df['dt'],scale = tscale ).unique() # add aggregate datetime into agg df 
        # declare dictionary with aggregate functions on given columns
        fun_d={  'open':lambda ser: ser.iloc[0],
                 'close':lambda ser: ser.iloc[-1],
                 'high':lambda ser: ser.max(),
                 'low': lambda ser: ser.min()
                }  
        # for each column in cols add a groupby result to aggregate_df 
        for col in cols:
            g=self.df[[col,dt_col ]].groupby([dt_col]) # groupby object on given column and tscale 
            x=g.apply(fun_d[col])[col].reset_index(name=col) # dataframe with results of apply on a groupby - not combined int oone line for clarity
            agg_df=agg_df.merge(x,left_on=dt_col,right_on=dt_col) # merge groupby-apply results into agg_df 
        return agg_df # dataframe with different aggregate functions applied on a different columns for a timescale 

        
if __name__=='__main__':
    csv_file= 'BTC-USD2022-06-04_2022-06-05.csv'
    #csv_file = 'BTC-USD2021-06-05_2022-06-05.csv'
    mdf=masterdf(csv_file=csv_file)
    raw_df=mdf.raw_df
    mdf.df=raw_df
    
    cols=['close','open','high','low']
    agg_df=mdf.aggregate(cols=cols,tscale=5)
    agg_df=mdf.aggregate(cols=cols,tscale=15)
    
    df=mdf.df
    s='2022-06-04T09:16:00.000000Z'

    format='%Y-%m-%dT%H:%M:%S.%fZ'
    czas=datetime.datetime.strptime(s,format)
    mask=df['dt']<=czas
    print(df[mask].dropna())
    
    print(agg_df)
    exit(1)

    
    # make a datetime from timestmpa 
    raw_df['dt']=mdf.compute_lambda(func='convert_dt',ser=raw_df['timestamp']) 
    raw_df['5min']=mdf.compute_lambda(func='floor_dt',ser=raw_df['dt'],scale = 5 ) # floor datetime to scale 
    
    highs_ser=raw_df[['high','5min']].groupby(['5min']).max().reset_index()
    print(raw_df['5min'])
    print(highs_ser)
    cols=['open','close','timestamp','dtt']
    print(mdf.df.columns)
    mdf.aggregate(cols=cols,tscale =5 )


if __name__=='__main__x':
    csv_file= 'BTC-USD2022-06-04_2022-06-05.csv'
    csv_file = 'BTC-USD2021-06-05_2022-06-05.csv'
    mdf=masterdf(csv_file=csv_file)
    df=mdf.df
    raw_df=mdf.raw_df
    
    candles=raw_df['close']-raw_df['open']
    candles_zscore=mdf.compute_lambda(func='roll_zscore',ser=candles,window=100)

    plt.hist(candles_zscore,bins=100,density=True)
    plt.show()
    exit(1)
    window_d={'long':100,'medium':50,'short':10}
    
    #df['sod']=mdf.compute_lambda(func='compute_sod',ser=raw_df['timestamp'])
    df['open_n']=mdf.compute_lambda(func='norm_roll_mean',ser=raw_df['open'],window=window_d['long'] ) # normalization 
    df['close_n']=mdf.compute_lambda(func='norm_roll_mean',ser=raw_df['close'],window=window_d['long'])
    
    df['close_std']=mdf.compute_lambda(func='roll_std',ser=df['close_n'],window=window_d['long'])
    df['close_n_ewm']=mdf.compute_lambda(func='ewm_mean',ser=df['close_n'],window=window_d['long']) # normalized close ema 
    
    df['ewm_distance']=mdf.replace_na( df['close_n']-df['close_n_ewm'],value=0,inplace=False)            
    # distance from normalized close to ema 
    area=pd.Series( integrate.cumtrapz( df['ewm_distance']))
    df['ewm_dist_area']=area 
    mdf.replace_na(ser= df['ewm_dist_area'],value=df['ewm_dist_area'].iloc[-2] ,inplace=True)
    
    df.dropna(how='any')
    # params - distance, distance integral, std 
#    slope, intercept, r_value, p_value, std_err = stats.linregress(df)
    
    df=df.iloc[200:2000]
    index=df.index

    fig,ax=plt.subplots(1,1)
    #ax[0].plot(index,df['close_n']/max(df['close_n']),'-or',index,df['close_n_ewm']/max(df['close_n_ewm']),'-ob')
    #ax[1].plot(index,df['ewm_distance']/max(df['ewm_distance']),'o-')
    #ax[2].plot(index,df['ewm_dist_area']/max(df['ewm_dist_area']),'ok-')
    ax.plot(index,df['close_n']/max(df['close_n']),'-or',
                index,df['close_n_ewm']/max(df['close_n_ewm']),'-ob',
                index,df['ewm_distance']/max(df['ewm_distance']),'.k-',
                index,df['ewm_dist_area']/max(df['ewm_dist_area']),'.g-',
                index,df['close_std']/max(df['close_std']),'.y-'
     )  
    ax.legend(['close','close_ema','distance','area','std'])
    ax.grid(True)
    #ax[1].grid(True)
    #ax[2].grid(True)
    
    
    plt.show()
    exit(1)

#

#pa=[10,20,30,40,50,60,70,60,50,60,50,40,30,20,30,40,40,40,50,60,50,40]
#
#ema = [sum(pa) / len(pa)] # first item of ema 
#sm=1/1
#for i,p in enumerate(pa[1:]):
#    ema.append((p * (sm / (1 + i))) + ema[-1] * (1 - (sm / (1 + i))))
    




#fig,ax=plt.subplots(2,1)
#ax[0].plot(pa,'o')
#ax[0].plot(ema,'o-')
#plt.show()