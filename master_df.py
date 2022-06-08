# to do RSI, MACD, boeillinger bands 

# this code defines master df which i shall use as a dataset for ai stuff 
import pandas as pd 




class masterdf:
    def __init__(self,csv_file:str = 'BTC-USD2021-06-05_2022-06-05.csv'):
        self.raw_df=pd.read_csv(csv_file,lineterminator=';') # read csv to df 
        self.mdf=pd.DataFrame() # master df 
        self.mdf.index=self.raw_df.index
        self.bcols=['open','close','low','high','epoch']
        
    def todos(self):
        # zscores on rollings and emas on 3 timeframes
        # rsi 
        # macd 
        # boilinger bands 
        # green red          
        pass 
    
    def add_col(self,colname : str ,
                ser : pd.Series,
                normalize : bool = False ,
                zscorize: bool = False):
        # adds column to mdf 
        # normalize - normalizes series 
        # zscorize - zscorizes series 
        if normalize:
            ser=self.normalize(ser)

        if zscorize:
            ser=self.zscorize(ser)
        self.mdf[colname]=ser
        
    def drop_col(self,colname: str): # pops column 
        self.mdf.drop(columns=[colname])
        
    def normalize(self, ser: pd.Series):
        return ser/ser.max()
    
    def zscorize(self, ser: pd.Series):
        return (ser-ser.mean() ) / ser.std()
        
    def make_mdf(self): # example mdf maker 
        self.add_col('epoch_n', self.normalize(self.raw_df['epoch']))
        self.add_col('open_z', self.zscorize(self.raw_df['open']),normalize=True,zscorize=True)
        self.add_col('close_z', self.zscorize(self.raw_df['close']),normalize=True,zscorize=True)
        self.add_col('high_z', self.zscorize(self.raw_df['high']),normalize=True,zscorize=True)
        self.add_col('low_z', self.zscorize(self.raw_df['low']),normalize=True,zscorize=True)


mdf=masterdf()
mdf.add_col('epoch',mdf.raw_df['epoch'])
mdf.make_mdf()

#mdf.compute_normalized_cols()
#ndf=mdf.compute_normalized_cols()
print(mdf.mdf)