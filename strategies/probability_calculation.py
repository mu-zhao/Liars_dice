import numpy as np 
import time
from scipy.stats import binom

def add_distribution(d1,d2):
    """This function  calculate distribution of two independent random varible. It is convolution (polinomial 
    product rule)
    When d1,d2 have different numbers of columns, d1 has 1 column.
    Arguments:
        d1 {2d array} -- discrete distribution of X
        d2 {2d array} -- discrete distribution of Y
    
    Returns:
        [list] -- distribution of (X+Y)
    """
    d=np.zeros((len(d1)+len(d2)-1,6))
    for i in range(len(d1)):       
        d[i:i+len(d2)]+=d2*d1[i]     #d1 can have the same number of columns as d2 or just has one column.
    return d 

def aggregate_distribution(D):
    """This function takes a list of distribution, returns the aggregate distribution. 
    
    Arguments:
        D {List of array} -- list of individual prob distribution, not cumulative
    
    Returns:
        numpy array -- aggregate distribution 
    """
    d=D[0]
    for i in D[1:]:
        if len(i)<len(d):   # run faster
            d=add_distribution(i,d)
        else:
            d=add_distribution(d,i)
    return d 


def call_belief(agg_player_dist,agg_others_dist,call_level):#they are cumulative dist
    
    critical_value=np.sum(agg_others_dist>=call_level,axis=0)-1
    call_dist=np.zeros((len(agg_player_dist)+len(agg_others_dist)-1,6))
    
    for i in range(6):
        call_dist[:critical_value[i],i]=0
        call_dist[critical_value[i]:critical_value[i]+len(agg_player_dist),i]=1-agg_player_dist[:,i]
        call_dist[critical_value[i]+len(agg_player_dist):,i]=1

    return call_dist 

def generate_init_dist(num_dice,f,cumulative=True):
    xrange=np.arange(num_dice+1)-cumulative
    agg_dist=np.zeros((num_dice+1,6))
    agg_dist[:num_dice+1,0]=f(xrange,num_dice,1/6)
    l=f(xrange,num_dice,1/3)
    for i in range(1,6):
        agg_dist[:,i]+=l
    return agg_dist

def get_legit_bids(bid):
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

#def best_response(last_bid,player_rollout,others_agg_dist,next_player_call_belief):  # this function will be called lots of times, so it has to be fast
#    if last_bid[0]>=player_rollout[last_bid[1]]+len(others_agg_dist):  # rollout is aggregated 
#        return [0]
#    elif last_bid[0]<=player_rollout[last_bid[1]]:
#        payoff=-1
#        response=[0]
#    else:
#        payoff=-others_agg_dist[last_bid[0]-player_rollout[last_bid[1]],last_bid[1]]
#        response=[0]
#    pay_list=[payoff]
#    response_list=[response]
#    for i,num in enumerate(get_legit_bids(last_bid)):
#        if num>=player_rollout[i]+len(others_agg_dist):
#            continue
#        elif num<=player_rollout[i]:
#            return [num,i] 
#        else:
#            p=(others_agg_dist[num-player_rollout[i],i]-1)*next_player_call_belief[num-player_rollout[i],i]
#         
#    return response 
def best_response(last_bid,rollout,others_agg_dist,next_player_call_belief):
    r=rollout[0]+rollout
    r[0]=rollout[0]
    result=np.ones((len(others_agg_dist)+int(sum(rollout)),6))
    for i in range(6):
        result[r[i]:r[i]+len(others_agg_dist),i]=others_agg_dist[:,i]
        result[r[i]+len(others_agg_dist):,i]=0
    payoff=(result-1)*next_player_call_belief # simple payoff of rasie
    payoff_call_liar=-result[last_bid[0],last_bid[1]] # simple payoff call liar 
    if payoff_call_liar==0:
        return [0]
    for i, bid in enumerate(get_legit_bids(last_bid)):
        payoff[:bid,i]=-1
    s=np.max(payoff)
    if s<=payoff_call_liar:
        return [0]
    payoff=payoff.flatten()
    prob=(payoff>=s*1.1)+(payoff>payoff_call_liar)*(s/payoff_call_liar)**2
    prob/=np.sum(prob)
    index=np.random.choice(np.arange(len(prob)),p=prob)
    return [index//6,index%6]
    
        
class AggregateDistribution: #notice they are all common knowledge
    def __init__(self,player_dice,others_dice,call_level):
        self.dice=player_dice
        self.call_level=call_level
        self.expectation=np.zeros(6)+player_dice/3
        self.expectation[0]/=2
        self.std=np.zeros(6)+np.sqrt(2*player_dice)/3
        self.std[0]=np.sqrt(5*player_dice)/6
        self.agg_dist=generate_init_dist(player_dice,binom.pmf,False)
        self.agg_cumulative_dist=generate_init_dist(player_dice,binom.sf)
        self.others_agg_dist=generate_init_dist(others_dice,binom.sf)
        self.call_dist=call_belief(self.agg_cumulative_dist,self.others_agg_dist,self.call_level)
       
        
    def update(self,outcome,dist):
        self.agg_dist=np.zeros_like(self.agg_dist)
        self.agg_cumulative_dist=np.zeros_like(self.agg_cumulative_dist)
        for i,rollout in enumerate(outcome):           #update dist
            self.agg_dist[rollout[0],0]+=dist[i]
            for j in range(1,6):
                self.agg_dist[rollout[j]+rollout[0],j]+=dist[i]
        self.agg_cumulative_dist=self.agg_dist[::-1].cumsum(axis=0)[::-1]  #update cumulative dist
        self.expectation=np.sum(self.agg_dist*np.arange(self.dice+1).reshape(-1,1),axis=0)
        second_moment=np.sum(self.agg_dist*(np.arange(self.dice+1).reshape(-1,1)**2),axis=0)
        self.std=np.sqrt(second_moment-self.expectation**2)
        print(self.expectation)
        
    def update_belief(self,belief_agg_dist): #belief_agg_dist is a list of players' agg dist
        self.others_agg_dist=aggregate_distribution(belief_agg_dist)[::-1].cumsum(axis=0)[::-1]
        self.call_dist=call_belief(self.agg_cumulative_dist,self.others_agg_dist,self.call_level)
      
        
                
                

    
class DistributionBelief:
    def __init__(self,player_dice,total_dice,call_level,bluff):
        prob=np.zeros(player_dice+1)
        prob[1:]=np.add.accumulate(np.log(np.arange(1,player_dice+1))) # to calculate distribution 
        outcome=np.empty(6,dtype=int)
        distribution=[]
        l=[0]*6  #iterator
        for l[0] in range(0,player_dice+1):    
            for l[1] in range(0,player_dice+1-sum(l[:1])): 
                for l[2] in range(0,player_dice+1-sum(l[:2])):
                    for l[3] in range(0,player_dice+1-sum(l[:3])):
                        for l[4] in range(0,player_dice+1-sum(l[:4])):
                            l[5]=player_dice-sum(l[:5])
                            p=np.exp(prob[player_dice]-sum([prob[i] for i in l])-player_dice*np.log(6))
                            outcome=np.vstack((outcome,l))
                            distribution.append(p)
        self.bluff=bluff
        self.total_dice=total_dice
        self.dice=player_dice
        self.outcome=outcome[1:]
        self.distribution=np.array(distribution)
        self.agg_info=AggregateDistribution(player_dice,total_dice-player_dice,call_level)
        
    def bayesian_inference(self,last_bid,previous_bid,next_player_call_belief):
        condon_prob=np.zeros_like(self.distribution)
        result=np.ones((self.total_dice+1,6))
        for index,rollout in enumerate(self.outcome):
            r=rollout[0]+rollout
            r[0]=rollout[0]
            for i in range(6):
                result[r[i]:r[i]+len(self.agg_info.others_agg_dist),i]=self.agg_info.others_agg_dist[:,i]
                result[r[i]+len(self.agg_info.others_agg_dist):,i]=0
            if previous_bid is None:
                payoff_call_liar=-1
            else:
                payoff_call_liar=-result[previous_bid[0],previous_bid[1]] # payoff call liar squared
            if payoff_call_liar<0:
                payoff=(result-1)*next_player_call_belief
                payoff_last_bid=payoff[last_bid[0],last_bid[1]]
                if payoff_last_bid>payoff_call_liar:
                    for i, bid in enumerate(get_legit_bids(previous_bid)):
                        payoff[:bid,i]=-1
                    condon_prob[index]=1/np.sum(payoff>(payoff_last_bid-0.001))
        posterior_dist=self.distribution*condon_prob
        posterior_dist/=np.sum(posterior_dist) #normalize
        self.distribution=self.distribution*self.bluff+posterior_dist*(1-self.bluff)
        
 
        
    def update_belief_about_player(self):
        self.agg_info.update(self.outcome,self.distribution)
    def update_player_belief_about_others(self,players_agg_dist):
       self.agg_info.update_belief(players_agg_dist)
    
    def calibrate_bluff(self,ture_rollout,bid):
        pass
            
            
    
    
    
    
    
    
    
class CommonResponseBelief:
    def __init__(self,dist_player,dist_rest):
        pass
        
        
        
