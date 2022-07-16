import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 

def myplot(x1y1 : list,x2y2 : list = [], leg : list = [[1,2],[3,4]]): # plots x1y1 and x2y2 where xiyi is  -> [ [xi,yi],[xj,yj],[xk,y,],]
    fig,ax=plt.subplots(2,1)
    colors=['r','g','b','k','y','m','r','g','b','k','y','m']
    lines=[]
    for i in range(0,len(x1y1)):
        x2=x1y1[i][0]
        y2=x1y1[i][1]
        line, = ax[0].plot(x2,y2,'x-' ,label=leg[0][i], color=colors[i]) 
        lines.append(line)
    ax[0].legend( handles = [i for i in lines] )        
    lines2=[]
    for i in range(0,len(x2y2)):
        x2=x2y2[i][0]
        y2=x2y2[i][1]
        line, = ax[1].plot(x2,y2,'-',label=leg[1][i] ,color=colors[i])
        lines2.append(line)
    ax[1].legend( handles = [i for i in lines2] )
    ax[0].grid(True)
    ax[1].grid(True)
    plt.show()


def myplot_df(df : pd.DataFrame, x1 : str, y1: list, x2: str ='', y2: list = []):
    
    if x1 == 'index':
        x1=df.index
    if x2 == 'index':
        x2=df.index
    
    x1y1= [ [x1,df[y] ] for y in y1  ]

    if y2==[]:
        myplot(x1y1,[])
        return 

    x2y2 = [ [ x2, df[y]] for y in y2  ]
    myplot(x1y1,x2y2, leg = [y1,y2] )