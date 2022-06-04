
# The Poisson distribution describes the probability of obtaining k successes during a given time interval.
# If a random variable X follows a Poisson distribution, then the probability that X = k successes can be found by the following formula:
# P(X=k) = λk * e– λ / k!
# where:
# λ: mean number of successes that occur during a specific interval
# k: number of successes
# e: a constant equal to approximately 2.71828

# A Poisson experiment is an experiment that has the following properties:
# -The number of successes in the experiment can be counted.
# -The mean number of successes that occurs during a specific interval of time (or space) is known.
# -Each outcome is independent.
# -The probability that a success will occur is proportional to the size of the interval.
#   this one seems particularly important 


# curious mind might who doesn't know about poisson limit theorem wonder if any population's percentile group follows a poisson distribution 
# in less confusing terms - whenever there is gaussian distribution you can cut off top x% and check if number of hits for this group follow 
# poisson distribution with x*N expected value so let's check if this happanes 

from scipy.stats import norm
from scipy.stats import poisson
import funs as f
import pandas as pd  
import numpy as np 
import matplotlib.pyplot as plt


# As noted above the idea is to run experiment N times and check how many out of n measurements per experiment fell into given percentile
# henceforth for n=1000 and 99percentile (alpha=0.01) one should expect to obtain 10 measurements for one experiment
# for n=1000 and cutoff = 0.005 one should expect to see 5 measurements above(below) this cutoff

def run_experiments(n=1000,alpha=0.01,N=100): # run_experiments(n=1000,alpha=0.005,N=10000):
    events=[]           # event - number of measurements that fall in given percentile 
    for i in range(N):  # run experiement N times 
        #df=pd.DataFrame({'pdf':norm().pdf(norm.rvs(size=n))}) # generate normal rvs 
        df=pd.DataFrame()
        df['rvs']=norm.rvs(size=n)
        df['pdf']=norm().pdf(df['rvs'])
        df['cdf']=norm().cdf(df['rvs'])
        df['events']=df['pdf'].where(df['pdf']<=alpha)
        
        events.append(len(df.where(df['cdf']<=alpha).dropna(how='any'))) #save how many fell into a percentile
    return events,df


if 1: # calculate df - may take some time depending on settings 
    print('runnign experiments')
    events,df=run_experiments()

if 0: # save data to csv  to csv so u dont have to calculate it everytime
    print('saving csv to file ')
    psn_csv='C:\\Users\\zdune\\Documents\\vsc\\gh\\tradebot\\random\\psn_csv.csv' # save to csv 
    #df=pd.DataFrame({'events':events_list})
    #pd.DataFrame({'events':events}).to_csv(psn_csv,index=False)
    df.to_csv(psn_csv,index=False)
    
if 0: #  read from vsv  
    print('reading csv from file ')
    psn_csv='C:\\Users\\zdune\\Documents\\vsc\\gh\\tradebot\\random\\psn_csv.csv' # save to csv 
    df=pd.read_csv(psn_csv) # read from csv 


if 1: # plot stuff
    fig,ax=plt.subplots(1,1)   # create plots
    bins=[min([0,min(events)]),min([20,max(events)]) ]  
    ax.set_xticks([i for i in range(bins[1])]) # make sure ticks are ok 
    ax.hist(pd.DataFrame({'events':events}),bins=bins[1])        # histogram plot 
    ax.grid(True) # grid is important in plotting 
#    plt.show() # showing the plot is also important 


if 1: # plot other stuff 
    fig,[ax1,ax2]=plt.subplots(2,1)
    ax1.plot(df['rvs'],df['pdf'] ,'.')
    ax2.plot(df['rvs'],df['cdf'],'.')
    ax1.grid(True)
    ax2.grid(True)
    print('did you check null hypothesis?')
    plt.show()



plt.show()
    