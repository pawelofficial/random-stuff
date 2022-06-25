from sklearn import linear_model
import random 
 
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd 

# make some data that shouldn't be fit with linear models

def line_is_a_line(): # a line is a line 
    N=100
    R=250
    x=[i for i in range(N)]
    f= lambda x: (x-25)*(x-67)
    y=[f(i)+ random.randint(0,R) for i in range(N)]
    x=np.array(x).reshape(-1,1)
    y=np.array(y).reshape(-1,1)
    # make models 
    reg_ord = linear_model.LinearRegression().fit(x,y)
    alpha=0.5
    reg_ridge=linear_model.Ridge(alpha=alpha).fit(x,y)
    reg_lasso=linear_model.Lasso(alpha=alpha).fit(x,y)
    # predict stuff 
    pred_y_ord=reg_ord.predict(x)
    pred_y_ridge=reg_ridge.predict(x)
    pred_y_lasso=reg_lasso.predict(x).reshape(-1,1) # well...
    # plot stuff 
    X=np.concatenate((x,x,x,x),axis=1)
    Y=np.concatenate((y,pred_y_ord,pred_y_ridge,pred_y_lasso),axis=1)
    return X,Y

# 101 -> let's fit linear models to some real world dataa
# 102 -> let's find a linear model that can be reasonably well fit to any day and let's takie a look at histogram of it's variables 
# then use median of those variables, if the histogram is pretty and let's see if it can predict stuff well
# prior to doing that one should get rid off very nonlinear events in the data, idea is to filter out candles that are in 99th percentile and then stitch it so pa is continous
# aka making big candles disappear 
# current ideas for independent variables, note that those need to be based on history, not current close, maybe a current open will do but
    # ema - it is history 
    # ema std - uses history 
    # area between ema and closes - how oversold / overbought is history 
    # to do: sentiment scrapping from coin telegraph 

    
f_ewm = lambda ser,window: ser.ewm(span=window).mean() # ewm mean 
f_std = lambda ser,window: ser.ewm(span=window).std() # ewm std 
f_diff = lambda ser,n: np.diff(ser,n,prepend = ser[:n]) # derivative 

df=pd.read_csv('BTC-USD2022-06-04_2022-06-05.csv',lineterminator=';').dropna(how='any')
# x1 -> close  - close ema 20 
# x2 -> std on 100 window 
# x3 -> volume 

window = 100 
df['close_n'] = ( df['close']-min(df['close']))/(max(df['close']) - min(df['close'])) # normalized close 
df['ema_close']=f_ewm(df['close_n'],window)      # close ema 
df['ema_close_diff']=f_diff(df['ema_close'],25) # derivative  of ema_close 
df['ema_close_diff2']=f_diff(df['ema_close_diff'],5) # second derivative of ema_close 

x=df.index
x1=diff.index
plt.plot(x,df['close_n'],x,df['ema_close'],x1,diff)
plt.show()
exit(1)

df['volume']=df['volume']/df['volume'].mean()

window=100
mydf=pd.DataFrame({'x0':np.array(df.index),
                   'x1':np.array(df['close'] - df['ema_close']),   # x1 -> close - ema close 
                   'x2':np.array(f_std(df['close'],window)),
                   'x3':np.array(df['volume'] - f_ewm(df['volume'],window)),
                   'y':np.array(df['close'])
                   }).dropna(how='any')



#X=np.concatenate((mydf['x1'](-1,1),mydf['x2'],mydf['x3']),axis=1)
#Y=np.array(mydf['close'])

X=mydf[['x1','x2','x3']]
Y= mydf['y'] 
lin_reg = linear_model.LinearRegression().fit(X,Y)
ridge_reg = linear_model.Ridge(alpha=0.5).fit(X,Y)
lasso_reg = linear_model.Lasso(alpha=0.1).fit(X,Y)
y_pred=lin_reg.predict(X)

print(lin_reg.score(X,Y),ridge_reg.score(X,Y),lasso_reg.score(X,Y))


if 1: # plot 
    fig,ax=plt.subplots(1,1)
    #ax.set_title(f"r2 {round(r2_score(y,pred_y),3) }, msq: {round(mean_squared_error(y,pred_y),3)} ")
    ax.set_title('a line is a line')
#    X,Y=line_is_a_line()
#    ax.plot(mydf['x0'],mydf['y'],mydf['x0'],y_pred)
    ax.plot(mydf['x0'],mydf['x1']/max(mydf['x1']),
            mydf['x0'],mydf['x2']/max(mydf['x2']),
            mydf['x0'],mydf['y']/max(mydf['y']),)
    ax.legend(['x1','x2','x3','y'])
    ax.grid(True)
    plt.show()