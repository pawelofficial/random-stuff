# this suer ugly code checks if pumps on btc follow poisson distribution
# in other words - is there an expected number of pumps where pumps are defined as top nth percentile of current
# population of bitcorn candles 



from cgitb import reset
import matplotlib
from numpy import column_stack
import pandas as pd 
import datetime   
import numpy as np 
import matplotlib.pyplot as plt
# variables 
uma_90d='UMA-USD2022-03-06_2022-06-04.csv' # download those with tradebot\coinbase_api.py 
uma_1d='UMA-USD2022-06-03_2022-06-04.csv'
btc_1d='BTC-USD2022-06-04_2022-06-05.csv'
btc_90d='BTC-USD2022-03-07_2022-06-05.csv'
btc_7d='BTC-USD2022-05-29_2022-06-05.csv'
btc_1yr='BTC-USD2021-06-05_2022-06-05.csv'
#btc_1yr=btc_7d#'BTC-USD2022-06-04_2022-06-05.csv'
format='%Y-%m-%dT%H:%M:%S.%fZ'
    #cols=['timestamp','open','close','low','high','volume']
# functions 
    # truncates iso string datetime to day 
f_day= lambda x: datetime.datetime.strptime(x,format).\
    replace(hour=0, minute=0, second=0, microsecond=0)
    # truncates iso string datetime to hour 
f_hour=lambda x: datetime.datetime.strptime(x,format).\
    replace( minute=0, second=0, microsecond=0)
    # converfts string to datetime
f_dt= lambda x: datetime.datetime.strptime(x,format)
    # floors datetime to 5 minutes 
f_5 = lambda dt : dt - datetime.timedelta(
    minutes=dt.minute % 3,
    seconds=dt.second,
    microseconds=dt.microsecond)

# a lot of printing requires advanced printing function 
def printo(x,s=''):
    print(x)
    print('-------------',s)
    
# another advanced function to simplify showing histograms 
def histo(df,y):
    N=2
    fig,ax=plt.subplots(1,1)
    ax.hist(df[y],bins=100,density=True)
    rng=[min(df[y])//1,max(df[y])//1]
    ax.set_xlim(left=rng[0],right=rng[1])
    ax.grid(True)
    xticks=[i for i in np.arange(rng[0],rng[1] )] # range arange orange
    ax.set_xticks(xticks)
    
    plt.show()
    return
# another fun for plotting stuf with oneliners 
def ploto(df,y):
    fig,ax=plt.subplots(1,1)
    ax.plot(df.index,df[y],'o')
    ax.grid(True)
    plt.show()
    
# function returnign a df which is an aggregate on a tscale of raw data which is on 1min intterval 

def stonks(df,tscale: str = '5min'): # function aggregating stonks data to a tscale and returning agg_df 
    if tscale not in list(df.columns):
        print('tscale gotta be in incoming dataframe anon ')
        return
    highs=df[['high',tscale]].groupby([tscale]).max().reset_index() # hour max 
    opens=df[['open',tscale]].groupby([tscale]).first().reset_index() 
    closes=df[['close',tscale]].groupby([tscale]).last().reset_index() 
    lows=df[['low',tscale]].groupby([tscale]).min().reset_index() 
    
    days=df[['day',tscale]].groupby([tscale]).first().reset_index() 
    hours=df[['hour',tscale]].groupby([tscale]).first().reset_index() 
    
    agg_df=highs.merge(opens, on=tscale, how='outer').\
    merge(closes, on=tscale, how='outer').\
    merge(lows, on=tscale, how='outer').\
    merge(hours, on=tscale, how='outer').\
    merge(days, on=tscale, how='outer')
    agg_df.rename(columns={'high':'highs',\
        'open':'opens',\
        'close':'closes',\
        'low':'lows',\
        'day':'days','hour':'hours'},inplace=True)
    return agg_df


# oneliner for filtering a dataframe for specific day to simplify plotting 
def day_filter_df(df,day: str,column: str = 'days'):
    return df.where(df[column]==day).dropna()
    
# experimenting with various datasets 
data=uma_90d
data=uma_1d
data=btc_1d
data=btc_90d
data=btc_7d
data=btc_1yr
df=pd.read_csv(data,lineterminator=';')

# 1. add columns to dataframe on lowest gran 
df['day']=df['timestamp'].apply(f_day) 
df['hour']=df['timestamp'].apply(f_hour)
df['5min']=df['timestamp'].apply(f_dt).apply(f_5)
df['1min']=df['timestamp']

#2. make aggregate df 
tscale='5min'
agg_df=stonks(df,tscale) # aggregate dataframe to tscale 
agg_df['candles']=(agg_df['closes']-agg_df['opens'])/agg_df['closes']*100

#3. percentile gotta be calculated on a population, this is a population span - a day of data 
windows=len(agg_df.where(agg_df['days']=='2022-06-03').dropna()) # percentiles have to be calculated on rolling which for daily has different len depending on tscale 
# 4. it's late anon  so let's do this this way
p99=99
p98=98
p97=97
#calculating column of a population percintiles 
agg_df['p99']=agg_df['candles'].rolling(window=windows).apply(lambda x: np.percentile(x,p99))
agg_df['p98']=agg_df['candles'].rolling(window=windows).apply(lambda x: np.percentile(x,p98))
agg_df['p97']=agg_df['candles'].rolling(window=windows).apply(lambda x: np.percentile(x,p97))

# calculating column showing if given row is a pump or not 
agg_df['ispump99']=(agg_df['candles']>agg_df['p99']).apply(lambda x: int(x))
agg_df['ispump98']=(agg_df['candles']>agg_df['p98']).apply(lambda x: int(x))
agg_df['ispump97']=(agg_df['candles']>agg_df['p97']).apply(lambda x: int(x))

# plotting stuff 
fig,ax=plt.subplots(1,1)
ax.hist(agg_df[['ispump99','days']].where(agg_df['ispump99']==1).dropna().groupby('days').count(),color='red',bins=100,density=True)
ax.hist(agg_df[['ispump98','days']].where(agg_df['ispump98']==1).dropna().groupby('days').count(),color='green',alpha=0.5,bins=100,density=True)
ax.hist(agg_df[['ispump97','days']].where(agg_df['ispump97']==1).dropna().groupby('days').count(),color='blue',alpha=0.5,bins=100,density=True)
ax.set_xticks([i for i in np.arange(0,20)])
ax.set_title('you should see poisson distributions here Anon')
ax.grid(True)
#ax.legend( ['percentyl98'] )
ax.legend( ['99pcntl','99pcntl','99pcntl'] )
plt.show()

exit(1)
# some stuff below 
x=agg_df[['ispump','days']].where(agg_df['ispump']==1).dropna().groupby('days').count()

histo(x,'ispump')




print(x.to_string())
exit(1)

#
#'2022-06-03' #10 na 90 
#'2022-06-02' #27 na 90 
daycheck='2022-06-03' 
foo_df=day_filter_df(agg_df,daycheck)
print(foo_df)
printo(len(foo_df.where(foo_df['ispump']==1).dropna()),'pumps')

printo(foo_df.where(foo_df['ispump']==1).dropna())

#foo_df=agg_df
fig,ax=plt.subplots(1,1)
ax.hist(foo_df['candles'],density=True,bins=100)
ax.hist(foo_df['ispump']*foo_df['candles']  ,color='r',density=True,alpha=0.5,bins=100)
ax.set_ylim([0,15])
ax.grid(True)
plt.show()
exit(1)
print(foo_df)


# check if it's ok 
day_agg_df=day_filter_df(agg_df,daycheck)# filtered agg df to look at one day only 
perc=np.percentile(day_agg_df['candles'],99)
printo(perc,'day agg df perc')
day_agg_df['ispump']=day_agg_df['candles'].apply(lambda x: int(x>perc))
count_pumps=day_agg_df[['ispump',tscale]].groupby('ispump').count()
printo(count_pumps,'count pumps')


pumps_df=day_agg_df.where( day_agg_df['candles']>perc).dropna()
print(pumps_df)
exit(1)



exit(1)
fig,ax=plt.subplots(1,1)
ax.hist(day_agg_df['candles'],density=True)
ax.hist(pumps_df['candles'],color='r',density=True,alpha=0.5)
plt.show()

exit(1)
histo(day_agg_df,'candle')



# good idea to check if your data is complete
    #counts_df=df[['5min','day']].groupby('day').count()
    #print(counts_df.sort_values(by='5min'))
    #histo(counts_df,'5min')

exit(1)


printo(day_agg_df)
exit(1)
printo(df)



printo(agg_df)
exit(1)


highs=df[['high',tscale]].groupby([tscale]).max().reset_index() # hour max 
opens=df[['open',tscale]].groupby([tscale]).first().reset_index() 
closes=df[['close',tscale]].groupby([tscale]).last().reset_index() 
lows=df[['low',tscale]].groupby([tscale]).min().reset_index() 
days=df[['day',tscale]].groupby([tscale]).first().reset_index() 
hours=df[['hour',tscale]].groupby([tscale]).first().reset_index() 

agg_df=highs.merge(opens, on=tscale, how='outer').\
    merge(closes, on=tscale, how='outer').\
    merge(lows, on=tscale, how='outer').\
    merge(hours, on=tscale, how='outer').\
    merge(days, on=tscale, how='outer')

agg_df.rename(columns={'high':'highs','open':'opens','close':'closes','low':'lows','day':'days','hour':'hours'},inplace=True)
agg_df['pumps']=(agg_df['highs']-agg_df['opens']) / agg_df['opens'] * 100 

cols=['open','close','low','high','timestamp','5min']
printo(df[cols].where(df['hour']=='2022-04-21 09:00:00').dropna().sort_values(by='timestamp') )
exit(1)
printo(agg_df.sort_values(by='pumps'))
#histo(agg_df,'pumps')
exit(1)

#make pumps df 
perc=np.percentile(agg_df['pumps'],99)
 
#agg_df['pumps'].where(agg_df['pumps']>=1,other=0)
agg_df['ispump']=agg_df['pumps'].apply(lambda x: int(x>perc))

#pumps_df.dropna(how='any',inplace=True)
agg_df.sort_values(by=['ispump','hours','pumps'],ascending=False,inplace=True)
printo(agg_df,'agg_df')

cols=['days','ispump','opens','closes','highs']
hist_df=agg_df[cols].groupby(['days']).sum().reset_index()#
hist_df.sort_values(by='ispump',inplace=True)
printo(hist_df,'hist df')

random_df=1
histo(hist_df,'ispump')

exit(1)



pumps_df=agg_df.where(agg_df['ispump']==1).dropna()
pumps_df.sort_values(by='pumps',ascending=False,inplace=True)
pumps_df['index']=pumps_df.index+1

short_df=agg_df.iloc[pumps_df['index']]
short_df['move']=(short_df['closes']-short_df['opens'] ) / short_df['closes'] * 100
short_df.sort_values(by='move',inplace=True)

histo(pumps_df,'pumps')
exit(1)
histo(short_df,'move')

printo(short_df)
exit(1)
printo(pumps_df,'pumps df ')
exit(1)
# look at histogram of pumps
cols=['hours','ispump','pumps'] 
hist_df=agg_df[cols].groupby(['hours']).sum().reset_index()#
hist_df.sort_values(by='ispump',ascending=False,inplace=True)
printo(hist_df,'hist df')
#histo(hist_df,'ispump')

#look at random day 
random_df=df.where(df['day'] == '2022-05-11').dropna(how='any')

printo(random_df,'random df ')
ploto(random_df,'close')
#histo(hist_df,'pumps')
#histo(hist_df,'pumps')
exit(1)
printo(agg_df)
printo(pumps_df)
exit(1)
# stop and think my friend here 


df=df.merge(agg_df, on=tscale, how='outer') # merge dataframe with pumps into original dataframe 
cols=[tscale,'day','opens','closes','highs','pumps','ispump']

xdf=df[['day','ispump']].groupby(['day']).count()
printo(agg_df)
printo(df.where(df['day']=='2022-04-30').dropna())


exit(1)
printo(df[cols])
printo(df[cols].dropna(how='any').drop_duplicates())

exit(1)




printo(agg_df[agg_df['ispump'].notna()])

print(agg_df)
exit(1)
tscale='hour'
pumps_df=agg_df[['ispump',tscale]].groupby([tscale]).count().reset_index() 
print(pumps_df)
exit(1)
