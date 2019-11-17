# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 21:31:43 2019

@author: Mu
"""
from scipy.stats import binom 
import numpy as np
import time
t=time.process_time()
d={} 
for i in range(100):
    x=np.random.random((200,200))
    for i in x:
        for j in d:
            if j>0.5:
                j+=1
print(time.process_time()-t)

                