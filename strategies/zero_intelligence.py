import numpy as np 
import time
from strategies import common as cm
from scipy.stats import norm
def transform(x):
    if x<0:
        return 0
    elif x>1:
        return 1
    return x
    
class ZeroIntelligence:
    def __init__(self,conservativeness,aggressiveness,stochastic=0):
        self.conservativeness=transform(conservativeness)
        self.up_lim_factor=0.84-0.54*self.conservativeness
        self.aggressiveness=transform(aggressiveness)
        self.stochastic=stochastic
        self.intelligence=0
        self.expectation=None 
        self.goodbet=None 
    def preprocess(self,dice_result,ck):
        others_total_dice=ck.get_total_dice()-sum(dice_result)
        expected_dice=others_total_dice/3+dice_result+dice_result[0]
        expected_dice[0]/=2
        self.expectation=expected_dice
        std_0=np.sqrt(5*others_total_dice)/6  # the std of number of 0 
        std_1=np.sqrt(2*others_total_dice)/3  # the std of number of other denominations
        self.std=np.array([std_0 if i==0 else std_1 for i in range(6)])
        self.bid_up_lim=self.expectation+self.std*self.up_lim_factor
        first_bid_candidate=self.expectation-self.std*(1+np.random.random_sample())*0.5
        if ck.last_bid is None:
            probability=first_bid_candidate+np.abs(first_bid_candidate)
            probability/=sum(probability)
            demonination=np.random.choice(6,p=probability)
            num=max(1,int(first_bid_candidate[demonination]))
            self.first_bid=[num,demonination]
        Goodbet=np.array([[1,1]])
        num=1
        while num<=max(self.bid_up_lim):
            if num%2==0:
                Goodbet=np.concatenate((Goodbet,np.array([[num/2,0]]+[[num,i] for i in range(1,6)])[self.bid_up_lim>=num]))
            else:
                Goodbet=np.concatenate((Goodbet,np.array([[num,i] for i in range(1,6)])[self.bid_up_lim[1:]>=num]))
            num+=1
        self.goodbet=Goodbet[1:] 
        self.goodbet.astype(int)      # here self.goodbet is sorted by definition
        
    def reset(self):
        self.expectation=None  
        self.bid_up_lim=None
        self.first_bid=None
        self.goodbet=None
        self.std=None
        
    def update_goodbet(self,bid):
        if  self.goodbet is not None:
            if cm.compare_bids([self.goodbet[-1],bid]): # if the highest goodbet is no greater than bid
                self.goodbet=None          #then no bet is good
                return
            if not cm.compare_bids([self.goodbet[0],bid]): # if the lowest goodbet is larger than bid
                return        #all bets are good
            low=0       # we'll use binary search to find good bet
            high=len(self.goodbet)-1
            while high-low>1:
                mid=int((low+high)/2)
                if cm.compare_bids([self.goodbet[mid],bid]): # if self.goodbet[mid] is not a good bet 
                    low=mid
                else:
                    high=mid 
            self.goodbet=self.goodbet[high:]
        
    def bid(self,player_id,dice_result,private_dist,ck):
        if self.expectation is None:
            self.preprocess(dice_result,ck)
        if ck.last_bid is None:
            return self.first_bid
        if self.goodbet is None:
            return [0]
        self.update_goodbet(ck.last_bid)
        if self.goodbet is not None:
            z_score=[(bid[0]-self.expectation[int(bid[1])])/self.std[int(bid[1])] for bid in self.goodbet ]
            neutral_position=[sum(ck.dice)/3]*6
            neutral_position[0]/=2
            neutral_std=[ np.sqrt(2*sum(ck.dice))/3]*6
            neutral_std[0]=np.sqrt(5*sum(ck.dice))/6
            neutral_z_score=[ (bid[0]+0.5-neutral_position[int(bid[1])])/neutral_std[int(bid[1])] for bid in self.goodbet]
            prob=1-norm.cdf(np.array(z_score))*norm.cdf(np.array(neutral_z_score))
            if np.random.random()<self.stochastic:
                prob=pow(prob,1+5*self.aggressiveness)
                return self.goodbet[np.random.choice(len(self.goodbet),p=prob/sum(prob))].astype(int)
            else:
                return self.goodbet[np.argmax(prob)].astype(int)
        return [0]

    
            

        

    