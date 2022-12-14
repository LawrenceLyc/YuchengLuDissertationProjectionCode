# -*- coding: utf-8 -*-
"""rawdata.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12UhIut4qcQV4PIizRMT8XaEQNcNKoEzx
"""

import numpy as np

# import cPickle

import _pickle as cPickle
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

data = cPickle.load(open('/content/drive/MyDrive/dissertation project/time_200913_to_201013.p', 'rb'))

# choosing valid data
a = data[(data.latitude>0)&(data.longitude>0)]
data = a[(a.latitude<=360)&(a.longitude<=360)]

# choosing stationary sensor
keepcids = []# this is a list consists of channel id
for cid in set(data['channel_id']):
    static = np.mean(np.abs(np.diff(data[data['channel_id']==cid]['latitude'])))<0.0001
    if static: keepcids.append(cid)

dstatic = data.loc[data['channel_id'].isin(keepcids)]

# put the last sensor's information into df
sensor = dstatic[dstatic.channel_id==keepcids[59]]
sensor['created_at'] = pd.to_datetime(sensor['created_at'])
df = sensor.resample('60min', on='created_at').mean()
df = df[0:1]

# put all the sensors' information into df
# as each sensor has different created time, it is difficult to find a time at which all the sensors have values, I just pick the first row of each sensor dataframe
for x in range(len(keepcids)-1):
  sensor = dstatic[dstatic.channel_id==keepcids[x]]
  sensor['created_at'] = pd.to_datetime(sensor['created_at'])
  df1 = sensor.resample('60min', on='created_at').mean() # take values each hour and compute the average 
  df1 = df1[0:1] # pick the first line
  df = df.append(df1)

# df is the dataframe which consists of 60 different sensors' information
df

#plot it
latitude=list(df['latitude'])
longitude=list(df['longitude'])
pm2_5 = list(df['pm2_5'])
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(latitude, longitude, pm2_5, '.', alpha=1)
plt.show()

!pip install GPy

# Commented out IPython magic to ensure Python compatibility.
import GPy
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import random
import scipy.stats
from scipy.stats import invgamma



#real data test1

# Training Data
b = []
for x in range(len(latitude)):
  a = [latitude[x]]
  a.append(longitude[x])
  b.append(a)
X = np.array(b)

b = []
for x in range(len(pm2_5)):
  a = [pm2_5[x]]
  b.append(a)
y = np.array(b)

#fit the GP
k = GPy.kern.RBF(2) #<--EQ kernel
m = GPy.models.GPRegression(X,y,k)
m.optimize()

#plot it
m.plot()

m

"""After fitting, I can see from above that the parameter values are really really big compared to my synthetic data before.

Q: Are these values correct or valid?
"""







# calculate predmean nd predvar
predmean, predvar = m.predict(X)

# compute NLPD
NLPD = np.sum(-np.log(scipy.stats.norm(predmean, np.sqrt(predvar)).pdf(y)))

# compute ML
m.log_likelihood()

# sample 100 times for different lengthscales
results = []
#compute sum for all the MLs
# sum=0
# for ls in np.linspace(1,30,100):
#     m.rbf.lengthscale = ls 
#     ll = m.log_likelihood()
#     sum += ll
#for l in np.linspace(0,30,100): #compute for different lengthscales
for ls in np.linspace(1,30,100):
    m.rbf.lengthscale = ls
    ll = m.log_likelihood()
    results.append([round(ls,3),round(ll,3)])
    # results.append([round(ls,3),round(ll,3),round(ll/sum,3)])
results = np.array(results)

"""Here I just keep the variance and gaussian noise value after fitting and try different values for lengthscales. I think I can do a better program in the week end to try differentt values for both lengthscale and gaussian noise value together.

Q: Do I have to set the variance valuefirst? How to set it?Or just keep it as the one after fitting?
"""

results

"""I have a questions here. As you see, the ML values here are very close (for different lengthscales), so that if I sum them up and divide each by the sum, they will be very close, about 0.01 as I sample 100 times.

Q: How to solve it?
"""

data = np.array(pm2_5)

# definition for gaussian distribution
#??????
def average(data):
    return np.sum(data)/len(data)
#?????????
def sigma(data,avg):
    sigma_squ=np.sum(np.power((data-avg),2))/len(data)
    return np.power(sigma_squ,0.5)
#??????????????????
def prob(data,avg,sig):
    print(data)
    sqrt_2pi=np.power(2*np.pi,0.5)
    coef=1/(sqrt_2pi*sig)
    powercoef=-1/(2*np.power(sig,2))
    mypow=powercoef*(np.power((data-avg),2))
    return coef*(np.exp(mypow))

# for loop to plot

for x in range(len(predmean)):
  data = np.array(np.linspace(predmean[x]-np.sqrt(predvar[x]),predmean[x]+np.sqrt(predvar[x]),100))
  ave=average(data)
  sig=sigma(data,ave)
  x=np.arange(0,100,0.01)
  p=prob(x,ave,sig)
  r=random.random()
  g=random.random()
  b=random.random()
  plt.plot(x,p,color=(r,g,b), linewidth=1)

plt.grid()
plt.xlabel("apple quality factor")
plt.ylabel("prob density")
plt.title("Gaussian distrbution")
plt.show()