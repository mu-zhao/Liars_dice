# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 02:35:00 2019

@author: Mu
"""
import numpy as np
from scipy.stats import binom
from strategies.bayesian_inference import get_legit_bids
from strategies.probability_calculation import generate_init_dist
from strategies.simulation import initial_bid_candidates,Simulation



    
    

class EpsilonIntelligence:
    def __init__(self,call_level=1/3,tolerance=0.25,inital_bid_aggresiveness=0.6,infer=False,simulation=False):
        self.call_level=call_level
        self.init_bid=inital_bid_aggresiveness
        self.infer=infer
        self.simulation=simulation
        self.vinilla_call_belief=None
        self.tolerance=tolerance
        
    def bid(self,palyer_id,rollout,private_dist,ck):
        self.last_bid=ck.last_bid
        self.max_payoff=-1
        self.response=None
        self.bid_candidates=None
        self.rollout=rollout
        self.others_num_dice=sum(ck.dice)-sum(rollout)
        if self.vinilla_call_belief is None:
            self.preprocess()
        if self.last_bid is not None:
            p_liar=binom.sf(self.last_bid[0]-self.rollout[self.last_bid[1]]-1,self.others_num_dice,1/6+(self.last_bid[1]==0)/6)
            p_spot_on=binom.pmf(self.last_bid[0]-self.rollout[self.last_bid[1]],self.others_num_dice,1/6+(self.last_bid[1]==0)/6)
            payoff_call_liar=-p_liar
            payoff_call_spot_on=2*p_spot_on-1
            #print(payoff_call_liar,payoff_call_spot_on)
            if payoff_call_liar>=payoff_call_spot_on:
                self.max_payoff=payoff_call_liar
                self.response=[0]
            else:
                self.max_payoff=payoff_call_spot_on
                self.response=[1]
        self.get_bid_candidate()
        self.best_bid()
        return self.response
        
    def best_bid(self):
        for bid in self.bid_candidates:
            payoff=-binom.cdf(bid[0]-self.rollout[bid[1]]-1,self.others_num_dice,
                              1/6+(bid[1]==0)/6)*self.vinilla_call_belief[bid[0],bid[1]]
            if payoff>self.max_payoff:
                self.max_payoff=payoff
                self.response=bid
        
    def reset(self):
        self.vinilla_call_belief=None
        
    def preprocess(self):
        N=sum(self.rollout)+self.others_num_dice  #num of total dice
        self.vinilla_call_belief=np.zeros((1+N,6))
        self.bid_upper_lim=[]
        for i in range(6):
            p=1/6+(i!=0)/6
            crit=binom.isf(self.call_level,N,p)
            upper_dev=int(binom.isf(self.tolerance,N,p))
            self.bid_upper_lim.append(self.rollout[i]+upper_dev+self.rollout[0]*(i!=0))
            self.vinilla_call_belief[:,i]=binom.cdf(np.arange(-1,N)-crit,N,p)
        
            
    def get_bid_candidate(self):
        if self.last_bid is None:
            self.bid_candidates=initial_bid_candidates(self.rollout,self.others_num_dice,self.init_bid)
        lower_lim=get_legit_bids(self.last_bid)
        self.bid_candidates=[[i,j] for j in range(6) for i in range(lower_lim[j],self.bid_upper_lim[j])]
        