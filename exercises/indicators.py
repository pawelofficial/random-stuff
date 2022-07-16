import pandas as pd 
import helpfuns as hf
import matplotlib.pyplot as plt 
import numpy as np 
import random 

class indicators:
    def __init__(self,csv_file:str = 'BTC-USD2022-06-04_2022-06-05.csv'):
        self.raw_df=pd.read_csv(csv_file,lineterminator=';') # read csv to df 
        self.df=pd.DataFrame() # master df 
        self.norm_z = lambda x_grid,xi,sigma :\
            1/(sigma * np.sqrt (2* np. pi )) * np.exp ( -1/2 * ( (x_grid-xi)/sigma  )**2  )
            
        
        self.norm = lambda x_grid,xi,h : self.norm_z(x_grid,xi,h)
        
    def test_fun(self): # returns [xi,yi] for checking kde fits
        f= lambda x: x*x*np.cos(x)
        xi = np.arange(-20,20,0.1)
        yi = [f(x)+random.randint(-10,10) for x in xi]
        return [xi,yi]
        
        
    def nadaraya(self,x : float,Xi : list ,Yi: list, h:float ): # returns watson-nadaraya fit at x for Xi,Yi data 
        wi=np.zeros(len(Xi))
        for i,xi in enumerate(Xi):
            wi[i] = self.norm(x,xi,h)  / np.sum ( [self.norm(x,xj,h) for xj in Xi])
        return np.sum ( [ wi[i] * Yi[i]  for i in range(len(Xi))])
    
    def nadaraya_index(self,s : pd.Series, h:float ): # dataframe is not smart hence passing rolling index values and computing nadaraya with that 
        x=int(s.iloc[0])
        window_df=self.df.loc[s]#.copy(deep=True)  # window dataframe 
        y=self.nadaraya( x,list(window_df['index']),list(window_df['close']),h)
        
        #print(y, np.isnan(y))
        if np.isnan(y):
            print(1)
            input()
            y=np.average(window_df['close'])
        return y
    

        
        
if __name__=='__main__':
    ind=indicators()
    ind.raw_df=ind.raw_df.iloc[:].copy(deep=True)
    ind.df=ind.raw_df
    df=ind.raw_df
    window=30
    #df['nad']=df['index'].apply( lambda x: ind.nadaraya(x,xi,yi)  )
    if 0:
        x1,y1=ind.test_fun()
        df=pd.DataFrame({'close':y1,'x1':x1})
    
    df['index']=df.index
    ind.df=df.copy(deep=True)
    
    df['candle']=df['close']-df['open']
    df['std_rolling']=df['candle'].rolling(window=window).std()
    df['nad10']=df['index'].rolling(window = window).apply( lambda x: ind.nadaraya_index(x,5) ) # passing rolling index to a function that computes nadaraya 
    df['nad20']=df['index'].rolling(window = window).apply( lambda x: ind.nadaraya_index(x,10) ) # passing rolling index to a function that computes nadaraya 
    df['nad30']=df['index'].rolling(window = window).apply( lambda x: ind.nadaraya_index(x,15) ) # passing rolling index to a function that computes nadaraya 

    df['e1']=df['nad30']+df['std_rolling']*3 # sell 
    df['e2']=df['nad30']-df['std_rolling']*3 # buy 
    mask1=df['close']>df['e1']
    mask2=df['close']<df['e2']
    
#    df.dropna(how='any',inplace=True)
    print(df [mask1 | mask2] )
    df['buy']=df[mask1]['close']
    df['sell']=df[mask2]['close']
#    hf.myplot(x1y1=[[xi,yi]],x2y2=[[xi,df['nad']]]  )
    hf.myplot_df(df=df,x1='index',y1=['close','sell','buy' ],x2='index',y2=['close','e1','e2' ])      
#    hf.myplot(x1y1=[[xi,yi]],x2y2=[[x_grid,y]])    
    

    
    