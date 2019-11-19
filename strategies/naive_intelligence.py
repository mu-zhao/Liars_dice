import numpy as np 
import time
from scipy.stats import binom 
from strategies.probability_calculation import best_response,get_legit_bids

def good_call(bid,rollout):
    result=np.sum(rollout,axis=0)
    result[1:]+=result[0]
    return bid[0]>result[bid[1]]
    
def simulation(bid,rollout,players_dist_belief,simulation_time_limit=0.05):   # the lists here include the first player's info
    N=len(players_dist_belief)    #total number of players
    start_time=time.process_time()
    num_simulation=0
    simulation_record=np.zeros(N)  # number of players lose game
    while(time.process_time()-start_time<simulation_time_limit):
        simulated_rollout=rollout   # first player's rollout is known 
        for i in range(1,N):
            index=np.random.choice(np.arange(len(players_dist_belief[i].outcome)),p=players_dist_belief[i].distribution)
            simulated_rollout=np.vstack((simulated_rollout,players_dist_belief[i].outcome[index]))
        last_bid=bid
        i=1
        discount_factor=1
        steps=0
        while True:
            discount_factor*=0.8
            response=best_response(last_bid,simulated_rollout[i],players_dist_belief[i].agg_info.others_agg_dist,players_dist_belief[(i+1)%N].agg_info.call_dist)
            if response==[0]:
                if good_call(last_bid,simulated_rollout):
                    simulation_record[(i-1)%N]+=discount_factor
                else:
                    simulation_record[i%N]+=discount_factor
                break
#            elif steps>N+1:
#                simulation_record+=discount_factor/N
#                break
            else:
                last_bid=response
                i=(i+1)%N
                steps+=1
        num_simulation+=1
    print(bid,'....................',simulation_record,'|',num_simulation)
    return simulation_record/sum(simulation_record)
                
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
    return utility(players_dice+dice_change)

def squared_power(dice):
    return dice[0]**2/sum(dice**2)

def initial_bid_candidates(rollout,num_other_dice,aggresive):
    L=[]
    for i in range(6):
        p=(2-(i==0))/6
        upper=int(binom.isf(0.5-aggresive/2,num_other_dice,p))
        lower=max(1,int(binom.isf(0.5+aggresive/2,num_other_dice,p)))
        L+=[[rollout[i]+k,i] for k in range(int(lower),int(upper)+1)]
    return L 

def get_bid_candidate(bid,rollout,stats):
    res=[]
    lower_lim=get_legit_bids(bid)
    upper_lim=stats[0]+stats[1]*3+rollout
    for i in range(6):
        res+=[[k,i] for k in range(lower_lim[i],int(upper_lim[i])+1)]
    return res 

class NaiveIntelligence:
    def __init__(self,aggresive=0.8,simulation_time_limit=5):
        self.time_limit=simulation_time_limit
        self.aggresiveness=aggresive
        self.expected_power=[]
    def bid(self,player_id,rollout,private_dist,ck):
        belief_dist=ck.get_all_common_belief(player_id)
        player_in_game_dice=ck.get_player_in_game_dice(player_id)
        if ck.last_bid is None:
            bid_candidate=initial_bid_candidates(rollout,ck.get_total_dice(),self.aggresiveness)
            max_payoff=0
            response=None 
        else:
            p_liar=private_dist[ck.last_bid[0],ck.last_bid[1]]
            if ck.last_bid[0]>=ck.get_total_dice():
                p_spot_on=p_liar
            else:
                p_spot_on=p_liar-private_dist[ck.last_bid[0]+1,ck.last_bid[1]]
            payoff_call_liar=reward(player_in_game_dice,player_id,squared_power,True)*(1-p_liar)+reward(player_in_game_dice,player_id,squared_power)*p_liar
            payoff_spot_on=reward(player_in_game_dice,player_id,squared_power,True,True)*p_spot_on+reward(player_in_game_dice,player_id,squared_power,spot_on=True)*(1-p_spot_on)
            print('liar',payoff_call_liar,p_liar)
            print('s',payoff_spot_on,p_spot_on)
            if payoff_call_liar>payoff_spot_on:
                max_payoff=payoff_call_liar
                response=[0]
            else:
                max_payoff=payoff_spot_on
                response=[1]
            bid_candidate=get_bid_candidate(ck.last_bid,rollout,ck.get_others_stats(player_id))
        if len(bid_candidate)>0:
            t_lim=self.time_limit/len(bid_candidate)
            for bid in bid_candidate:
                sim_res=simulation(bid,rollout,belief_dist,t_lim)
                payoff_bid=payoff(sim_res,player_in_game_dice,squared_power)
                print(bid,'|',payoff_bid)
                if payoff_bid>max_payoff:
                    max_payoff=payoff_bid
                    response=bid
        self.expected_power.append(max_payoff)
        return response





    def reset(self):
        pass
        


