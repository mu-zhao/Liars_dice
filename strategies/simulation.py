# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 20:01:46 2019

@author: Mu
"""

import numpy as np 
import time
from scipy.stats import binom 
from strategies.bayesian_inference import get_legit_bids
from strategies.probability_calculation import generate_init_dist
def initial_bid_candidates(rollout,num_other_dice,aggresive):
    L=[]
    for i in range(6):
        p=(2-(i==0))/6
        upper=int(binom.isf(0.5-aggresive/2,num_other_dice,p))
        lower=int(binom.isf(0.5+aggresive/2,num_other_dice,p))
        L+=[[max(1,rollout[i]+k),i] for k in range(int(lower),int(upper)+1)]
    return L 

def get_bid_candidate(bid,private_dist,aggresive):
    upper_lim=np.sum(private_dist>=1-aggresive,axis=0)
    lower_lim=get_legit_bids(bid)
    return [[i,j] for j in range(6) for i in range(lower_lim[j],upper_lim[j]) ]



def squared_power(dice):
    return dice[0]**1.2/sum(dice**1.2)*100

def linear_power(dice):
    return dice[0]/sum(dice)

def reward(players_dice,utility,goodcall=False,spot_on=False,caller_id=0): # the reword for player 0
    N=len(players_dice)
    dice_change=np.zeros_like(players_dice)
    if goodcall:
        if spot_on:
            dice_change-=1
            dice_change[caller_id]=0
        else:
            dice_change[(caller_id-1)%N]=-1
    else:
        dice_change[caller_id]=-1
    return utility(players_dice+dice_change)

class Simulation:
    def __init__(self,bids,rollout,players_dice,players_dist_belief,response_principle,time_limit,blur,is_bayes_dist=True,
                 call_level=1/3,num_limt=2500,utility_f=squared_power,simple_minded=True):
        self.bids=bids
        self.rollout=rollout
        self.dice=players_dice     # all players dice, start with the player
        self.belief=players_dist_belief
        self.time_lim=time_limit
        self.utility=utility_f
        self.num_palyers=len(players_dist_belief)  #total number of players
        self.num_limit=num_limt
        self.response_principle=response_principle
        self.blur_judgement=blur
        self.call_level=call_level
        self.is_bayes_dist=is_bayes_dist
        self.simple_minded=simple_minded
        self.dice_lost=None
    def run(self,bid):   # the lists here include the first player's info
        start_time=time.process_time()
        num_simulation=0
        self.sim_error=0
        self.sim_record=np.zeros(self.num_palyers)
        step=0
        while(time.process_time()-start_time<self.time_lim and num_simulation<self.num_limit):
            self.sim_rollout=self.rollout   # first player's rollout is known 
            for i in range(1,self.num_palyers):
                if self.is_bayes_dist:
                    index=np.random.choice(np.arange(len(self.belief[i].outcome)),p=self.belief[i].distribution)
                else:
                    index=np.random.choice(np.arange(len(self.belief[i].outcome)),p=self.belief[i].prior_dist)
                self.sim_rollout=np.vstack((self.sim_rollout,self.belief[i].outcome[index]))
            self.last_bid=bid
            i=1
            discount=1
#            print('...............................................',self.last_bid)
#            print(self.sim_rollout)
            while True:
                step+=1
                discount*=1-0.3/np.sqrt(self.num_palyers)
                response=self.best_response(i)
                #print(i,response)
                if response==[0]:
                    if self.good_call():
                        self.sim_record[(i-1)%self.num_palyers]+=discount
                    else:
                        self.sim_record[i%self.num_palyers]+=discount
                    break
                else:
                    self.last_bid=response
                    
                    i=(i+1)%self.num_palyers
            num_simulation+=1
            self.sim_error=np.sqrt(self.sim_record[0]*(1-self.sim_record[0]/num_simulation))/num_simulation
        print(num_simulation)
#        print(bid,'....................',self.sim_record,'|',step/num_simulation,num_simulation)
#    
    
    
    def sim_payoff(self):
        pay=0
        if self.simple_minded:
            return  -self.sim_record[0]/sum(self.sim_record)
        for i in range(self.num_palyers):
            pay+=reward(self.dice,self.utility,caller_id=i)*self.sim_record[i]
        return pay/sum(self.sim_record), -self.sim_record[0]/sum(self.sim_record)

    def simulation_result(self):
        self.payoff=-1
        self.response=None
        for bid in self.bids:
            self.run(bid)
            payoff,lost=self.sim_payoff()
            #print(bid,'|',payoff)
            if payoff>self.payoff:
                self.payoff=payoff
                self.response=bid
                self.dice_lost=lost
                self.error=self.sim_error
        return self.response, self.payoff , self.dice_lost, self.error
            
    def best_response(self,player_id):
        if self.response_principle==0:
            return self.reasonable_call(player_id)
        elif self.response_principle==1:
            return self.naive_call(player_id)
        else:
            return self.simple_call(player_id)
     
        
    def good_call(self):
        self.sim_result=np.sum(self.sim_rollout,axis=0)
        self.sim_result[1:]+=self.sim_result[0]
        return self.last_bid[0]>self.sim_result[self.last_bid[1]]



    def reasonable_call(self,player_id):
        r=self.sim_rollout[player_id][0]+self.sim_rollout[player_id]
        r[0]=self.sim_rollout[player_id][0]
        N=sum(self.dice)
        if self.last_bid[0]>N-self.dice[player_id]+r[self.last_bid[1]]:
            return [0]
        result=np.ones((N+1,6))
        for i in range(6):
            result[r[i]:r[i]+len(self.belief[player_id].agg_info.others_agg_dist),i]=self.belief[player_id].agg_info.others_agg_dist[:,i]
            result[r[i]+len(self.belief[player_id].agg_info.others_agg_dist):,i]=0
        payoff=(result-1)*self.belief[(player_id+1)%self.num_palyers].agg_info.call_dist # simple payoff of rasie
        payoff_call_liar=-result[self.last_bid[0],self.last_bid[1]] # simple payoff call liar 
        if payoff_call_liar>10**(-8):
            return [0]
        for i, bid in enumerate(get_legit_bids(self.last_bid)):
            payoff[:bid,i]=-1
        s=np.max(payoff)
        if self.blur_judgement:
            if payoff_call_liar>=s or  np.random.sample()<1/np.sum(payoff>=payoff_call_liar):
                return [0]
            payoff=payoff.flatten()
            prob=(payoff>=s*1.1)+(payoff>payoff_call_liar*0.95)*(s/payoff_call_liar)**2
            prob/=np.sum(prob)
            index=np.random.choice(np.arange(len(prob)),p=prob)
        elif payoff_call_liar>=s:
            return [0]
        else:
            payoff=payoff.flatten()
            prob=(payoff>=1.05*s)+(payoff==s)
            prob=prob/np.sum(prob)
            index= np.random.choice(np.arange(len(payoff)),p=prob)
        return [index//6,index%6]



    def simple_call(self,player_id):
        r=self.sim_rollout[player_id][0]+self.sim_rollout[player_id]
        r[0]=self.sim_rollout[player_id][0]
        N=sum(self.dice)
        if self.last_bid[0]>N-self.dice[player_id]+r[self.last_bid[1]]:
            return [0]
        result=np.ones((N+1,6))
        for i in range(6):
            result[r[i]:r[i]+len(self.belief[player_id].agg_info.others_agg_dist),i]=self.belief[player_id].agg_info.others_agg_dist[:,i]
            result[r[i]+len(self.belief[player_id].agg_info.others_agg_dist):,i]=0
        payoff_call_liar=-result[self.last_bid[0],self.last_bid[1]] # simple payoff call liar 
        if payoff_call_liar>-1/4:
            return [0]
        candidate=get_legit_bids(self.last_bid)
        
        payoff=[]
        
        for i in range(6):
            if candidate[i]<=N:
                p=(2-(i==0))/6
                crit=binom.isf(1/3,N,p)
                payoff.append((1-result[candidate[i],i])*binom.cdf(-crit+candidate[i],N,p))
        if payoff:
            index=np.argmin(np.array(payoff))
            return [candidate[index],index]
        return [0]
                
    def naive_call(self,player_id):
        r=self.sim_rollout[player_id][0]+self.sim_rollout[player_id]
        r[0]=self.sim_rollout[player_id][0]
        N=sum(self.dice)
        other_dice=N-self.dice[player_id]
        if self.last_bid[0]>r[self.last_bid[1]]+other_dice:
            return [0]
        p_call_liar=binom.cdf(self.last_bid[0]-r[self.last_bid[1]]-1,other_dice,1/6+(self.last_bid[1]!=0)/6)
        odds=np.zeros((1+N,6))
        lower_lim=get_legit_bids(self.last_bid)
        for i in range(6):
            p=1/6+(i!=0)/6
            upper=int(binom.isf(0.15,other_dice,p))+r[i]
            lower=lower_lim[i]
            odds[lower:upper+1,i]=(1-binom.cdf(np.arange(-r[i]-1,-r[i]+N),
                              other_dice,p)*binom.cdf(np.arange(-1,N),N,p))[lower:upper+1]
        if p_call_liar> 0.7 or np.random.sample()<p_call_liar/(p_call_liar+np.sum(odds)):
            return [0]
        else:
            odds=(odds**3).flatten()
            odds/=np.sum(odds)
            #print('odd',odds)
            index=np.random.choice(np.arange(len(odds)),p=odds)
            return [index//6,index%6]
            
        

