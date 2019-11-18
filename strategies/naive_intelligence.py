import numpy as np 
import time
from probability_calculation import best_response,get_legit_bids

def good_call(bid,rollout):
    result=np.sum(rollout,axis=0)
    result[1:]+=result[0]
    return bid[0]>result[bid[1]]
    
def simulation(bid,rollout,players_dist_belief,simulation_time_limit=0.05):   # the lists here include the first player's info
    N=len(players_dist_belief)    #total number of players
    start_time=time.process_time()
    num_simulation=0
    simulation_record=np.zeros(N,dtype=int)  # number of players lose game
    while(time.process_time()-start_time<simulation_time_limit):
        simulated_rollout=rollout   # first player's rollout is known 
        for i in range(1,N):
            simulated_rollout=np.vstack((simulated_rollout,np.random.choice(players_dist_belief[i].outcome,p=players_dist_belief[i].distribution)))
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
    print(simulation_time_limit ,num_simulation)
    return simulation_record/num_simulation
                
def payoff(result_dist,players_dice,utility):
    pay=0
    for i in range(len(result_dist)):
        pay+=reward(players_dice,i,utility)*result_dist[i]
    return pay

def reward(players_dice,player_id,utility,goodcall=False,spot_on=False):
    N=len(players_dice)
    dice_change=np.zeros_like(players_dice)
    if goodcall:
        if spot_on:
            dice_change-=1
            dice_change[player_id]=0
        else:
            dice_change[(player_id-1)%N]=-1
    else:
        dice_change[player_id]=-1
    return utility(players_dice-dice_change)

def squared_power(dice):
    return dice[0]**2/sum(dice**2)

def initial_bid_candidates(rollout,num_other_dice,aggresive):
    L=[]
    for i in range(6):
        p=2-(i==0)
        lower,upper=binom.interval(aggresive,num_other_dice,p,loc=p*num_other_dice)
        L+=[[rollout[i]+k,i] for k in range(int(lower),int(upper)+1)]
    return L 


class NaiveIntelligence:
    def __inti__(self,simulation_time_limit=5):
        self.time_limit=simulation_time_limit
        self.expected_power=[]
    def bid(self,player_id,rollout,p_dist,ck):
        belief_dist=ck.get_all_call_belief(player_id)
        player_in_game_dice=ck.get_player_in_game_dice(player_id)
        if ck.last_bid is None:
            bid_candidate=initial_bid_candidates(rollout,ck.get_total_dice())
            t_lim=self.time_limit/len(bid_candidate)
            max_payoff=0
            response=None 
            for bid in bid_candidate:
                sim_res=simulation(bid,rollout,belief_dist,t_lim)
                payoff_bid=payoff(sim_res,player_in_game_dice,squared_power)
                if payoff_bid>max_payoff:
                    max_payoff=payoff_bid
                    response=bid
            self.expected_power.append(max_payoff)
            return response
        else:
            p_liar=
            payoff_call_liar=reward(player_in_game_dice,player_id,squared_power,True)*





    def reset(self):
        pass
        


