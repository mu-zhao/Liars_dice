# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 20:14:45 2019

@author: Mu
"""
import numpy as np
from scipy.stats import binom

def get_legit_bids(bid):  #could over flow
    if bid is None:
        return [1]*6
    L=np.zeros(6,dtype=int)
    if bid[1]==0:
        L[0]=bid[0]+1
        L[1:]=2*bid[0]
        return L
    else:
        L[0]=bid[0]//2+1
        L[1:bid[1]+1]=bid[0]+1
        L[bid[1]+1:]=bid[0]
    return L


def transition_prob(result,rollout,pre_bid,bid,call_belief):
    epsilon=0.001
    if pre_bid is not None:
        payoff_call_liar=-result[pre_bid[0],pre_bid[1]]
        if payoff_call_liar>-0.01:
            return 0
        payoff=(result-1)*call_belief
        for i,b in enumerate(get_legit_bids(pre_bid)):
            payoff[:b,i]=-1
        odds=1/(epsilon-payoff)-1/(1+epsilon)
        return odds[bid[0],bid[1]]/(np.sum(odds)+1/(epsilon-payoff_call_liar))
    elif result[bid[0],bid[1]]<1/3:
        return 0
    else:
         score=(1+(result-1)*call_belief)**2
         return score[bid[0],bid[1]]/np.sum(score)
        
def transition_prob_naive(result,rollout,pre_bid,bid,call_belief):
    r=rollout[0]+rollout
    r[0]=rollout[0]
    N=len(result)-1  #num of total dice
    other_dice=N-sum(rollout)
    odds=np.zeros((1+N,6))
    if pre_bid is not None:
        lower_lim=get_legit_bids(pre_bid)
    for i in range(6):
        p=1/6+(i!=0)/6
        upper=int(binom.isf(0.15,other_dice,p))+r[i]
        if pre_bid is None:
            lower=max(1,int(binom.isf(0.85,other_dice,p))+r[i])
        else:
            lower=max(1,lower_lim[i])
        odds[lower:upper+1,i]=(1-binom.cdf(np.arange(-r[i]-1,-r[i]+N),
                              other_dice,p)*binom.cdf(np.arange(-1,N),N,p))[lower:upper+1]
    odds=odds**(3+int(9/other_dice**2))
#    if sum(rollout)==1:
#        print(rollout,pre_bid,bid)
#        print(odds)
    if odds[bid[0],bid[1]]==0:
        return 0
    return odds[bid[0],bid[1]]/np.sum(odds)
        
    
    
        
      
 
    
            
        
    
