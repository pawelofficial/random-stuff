# here is some cookbook for pandas syntax 

import pandas as pd 
import numpy as np 
a=[1,2,3,4]
b=[5,6,7,8]
d={'a':a,'b':b,'e':1} 
df=pd.DataFrame(d)
l=[True,True,False,False]
print(df)

df.loc[0,'a']=-1
print(df)