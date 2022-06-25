from master_df import masterdf
from scipy import integrate
import numpy as np 
import matplotlib.pyplot as plt
from sklearn import linear_model
import pandas as pd 
from scipy import stats

# this does linreg regression for each day from csv data for btc and dumps the coefficients it found  
# to a csv so you can later take a look at the coefficients and check if they are cool or not 
# definitely not the most optimal way to do this exercise 
# to do:
#   - check how a variable made from ewm derivative does 
#   - do backtesting on stats model 
#           how do i do backtesting on inference though 

if __name__=='__main__':
# 1. get csv with data 
    csv_file= 'BTC-USD2022-06-04_2022-06-05.csv'
    csv_file='BTC-USD2022-05-29_2022-06-05.csv'
    #csv_file = 'BTC-USD2021-06-05_2022-06-05.csv'
    mdf=masterdf(csv_file=csv_file)
    sdf=mdf.df              
    raw_df=mdf.raw_df
    window=100

    sdf['timestamp']=mdf.compute_lambda(func='convert_dt',ser=raw_df['timestamp'])
    sdf['day']=sdf['timestamp'].apply(lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0))
    sdf['close']=raw_df['close']
    sdf['open']=raw_df['open']


    dayz=list(set(sdf['day'].astype('str') ))  # distinct days in dataframe 
    
    # dataframe with coefficients linreg came up with for each day 
    results_d={'a':[],'b':[],'c':[],'score':[] }
    results_df=pd.DataFrame(results_d) 
    if 0:
        dayz=[]
        print('not running loop')

    for d in dayz:
        mask=sdf['day'].astype('str')==d
        df=sdf[mask].copy(deep=True) # gotta work on a df not a copy of sdf 

        df['candles']=df['close']-df['open']  
        df['candles_zscore']=mdf.compute_lambda(func='roll_zscore',ser=df['candles'],window=window) 
        df['ewm_zscore']= mdf.compute_lambda(func='ewm_mean',ser=df['candles_zscore'],window=window )
        df['x0'] = df['ewm_zscore'] # x0 made just for fun 
        # x1 = zscore std 
        df['x1']=mdf.compute_lambda(func='roll_std',ser=df['ewm_zscore'],window=window)  
        # x2 -> distance from ewm 
        df['x2']= df['candles_zscore']-df['ewm_zscore']
        df['x1']=df['x2'] # using std for fitting returns super variable coefficient so let's just use x2 and x3 
        # x3 -> integral of distance to ewm
        df['x3']=mdf.compute_lambda(func='trapz',ser=df['x2'],window=window)
        input=['x1','x2','x3']
        output=['ewm_zscore']
        mydf=df.dropna(how='any')
        X=mydf[input].to_numpy()
        Y=mydf[output].to_numpy()
        lin_reg = linear_model.LinearRegression().fit(X,Y)
        y_pred=lin_reg.predict(X)
        if 0: # plot results for each day fren 
            fig,ax=plt.subplots(1,1)
            ax.plot(Y,'ok')
            ax.plot(y_pred,'or')
            plt.show()

        coefs=lin_reg.coef_[0]
 
        l=len(results_df)
        results_df.loc[l,:]=np.append(coefs, lin_reg.score(X,Y))
        print(results_df.loc[l,:])
 
    
# looks like coefficient for std  has huge variability which is not cool
# other two have low CV so they are ok  

df=pd.read_csv('ols_results.csv') # use csv to see coefficients for each day 
df=results_df # use current results_df 
zdf=(df-df.mean() ) / df.std() # zscore is advanced statistics 

fig,ax=plt.subplots(3,2)
ax[0,0].plot(zdf['a'],'o')
ax[1,0].plot(zdf['b'],'o' )
ax[2,0].plot(zdf['c'],'o' )
ax[0,1].plot(df['a']/df['a'].mean(),'o')
ax[1,1].plot(df['b']/df['b'].mean(),'o' )
ax[2,1].plot(df['c']/df['c'].mean(),'o' )

print(df)
plt.show()
