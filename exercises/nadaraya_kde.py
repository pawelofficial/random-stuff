import pandas as pd 
from master_df import masterdf
import matplotlib.pyplot as plt  
import numpy as np 
import random 

def plot(x1y1,x2y2 : list = []): # plots x1y1 and x2y2 where xiyi is  -> [ [xi,yi],[xj,yj],[xk,y,],]
    bounds=[-15,15] # plot bounds 
    # plot configs 
    ticks=np.arange(bounds[0],bounds[1],1)
    fig,ax=plt.subplots(2,1)
    ax[0].set_xlim(left=bounds[0],right=bounds[1])
    ax[1].set_xlim(left=bounds[0],right=bounds[1])
    ax[0].set_xticks(ticks)
    ax[1].set_xticks(ticks)
#plot x1y1 data 
    for i in range(0,len(x1y1)):
        x2=x1y1[i][0]
        y2=x1y1[i][1]
        ax[0].plot(x2,y2,'.')
# plot x2ye data 
    for i in range(0,len(x2y2)):
        x2=x2y2[i][0]
        y2=x2y2[i][1]
        ax[1].plot(x2,y2,'.')
# show plot 
    ax[0].grid(True)
    ax[1].grid(True)
    plt.show()

# data to fit 
x=np.linspace(-10,10,500)  #  x axis 
grid=np.linspace(-10,10,500)


# nadaraya watson estimator is basically this 
# you have your (Xi,Yi) raw data points
# you get yourself an x grid 
# you compute wi for each raw data point for given x  --> wi(x) 
# your estimation of y(x) = sum (wi * Yi) 
# wi is a pdf(x-Xi) / np.sum( [pdf(x-xj) for xj in Xi]   )
# aka it's a pdf for Xi / pdf for all Xis 
# gotta optimize this mess above and below but it's working ! 
N=50
noise=50
f= lambda x: x*x*np.cos(x)
Xi=[random.randint(-10,10) for i in range(N)]
eps=[1*random.randint(0,noise) for i in range(N)]
Y=[f(Xi[i])+eps[i] for i in range(N)]


sigma=1
norm_z = lambda x,mu,sigma : 1/(sigma * np.sqrt (2* np. pi )) * np.exp ( -1/2 * ( (x-mu)/sigma  )**2  )
norm= lambda x,mu : norm_z(x,mu,sigma) # norm od liczby 
norm_vec= lambda x,mu : [norm(xi,mu) for xi in x] # pdf for vec to save lines 


def y_x(x,Y=Y):
    w=np.zeros(len(Xi))
    y=np.zeros(len(Xi))
    for i in range( len(Xi) ):
        w[i]=norm(x,Xi[i]) / np.sum ( [ norm(x,xj ) for xj in Xi    ] )
        y[i] = w[i]*Y[i]
        
    return np.sum(y)     


y=[y_x(xi) for xi in grid]

# raw data 
x1y1=[[Xi,Y],[grid,y]]
x2y2 = [[grid,y]]

 

plot(x1y1,x2y2)