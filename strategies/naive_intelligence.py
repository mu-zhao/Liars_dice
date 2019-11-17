import numpy as np 
import time
from probability_calculation import best_response

def good_call(bid,rollout):
    result=np.sum(rollout,axis=0)
    result[1:]+=result[0]
    return bid[0]>result[bid[1]]
    
def simulation(bid,rollout,players_dist_belief,simulation_time_limit=0.5):   # the lists here include the first player's info
    N=len(players_dist_belief)    #total number of players
    start_time=time.process_time()
    num_simulation=0
    simulation_record=np.zeros(N,dtype=int)  # number of players lose game
    while(time.process_time()-start_time<simulation_time_limit):
        simulated_rollout=rollout   # first player's rollout is known 
        for i in range(1,N):
            simulated_rollout=np.vstack((simulated_rollout,np.random.choice(players_dist_belief[i].outcome,players_dist_belief[i].distribution)))
        i=1  #player id
        last_bid=bid
        while True:
            response=best_response(last_bid,simulated_rollout[i],players_dist_belief[i].agg_info.others_agg_dist,players_dist_belief[(i+1)%N].agg_info.call_dist)
            if response==0:
                if good_call(last_bid,simulated_rollout):
                    simulation_record[(i-1)%N]+=1
                else:
                    simulated_rollout[i]+=1
                break
            else:
                last_bid=response
                i=(i+1)%N
        num_simulation+=1
                



class NaiveIntelligence:
    def __inti__(self,num_dice):
        pass
    def bid(self):
        pass 


