import numpy as np 
import pandas as pd
from strategies.simulation import initial_bid_candidates,Simulation,get_bid_candidate,reward,squared_power,linear_power
from IPython.display import display, HTML
def good_choice(res,pay,rollout):
    if len(set(res))==3:
        r=rollout+rollout[0]
        d={}
        for i in res:
            if len(i)>1:
                d[i]=i[0]*(1+(i[1]==0))-r[i[1]]
        
        return list(min(d,key=d.get))
            
    if res[0]==res[1] or res[0]==res[2]:
        return list(res[0])
    else:
        return list(res[1])
                

def two_player_game(last_bid,rollout):
    pass

def time_limit(t_limit,dice):
    num=1
    for i in dice[1:]:
        num*=np.math.factorial(i)
        
class NaiveIntelligence:
    def __init__(self,aggresive=0.8,simulation_time_limit=2,num_limit=2000,response_principle=0,utility=squared_power,
                 blur=False,call_level=1/3,bayes_dist=True,simple_minded=True,advisor=True):
        self.time_limit=simulation_time_limit
        self.aggresiveness=aggresive
        self.expected_power=[]
        self.response_principle=response_principle
        self.num_lim=num_limit
        self.judgement=blur
        self.bayes_dist=bayes_dist
        self.utility=utility
        self.simple_minded=simple_minded
        self.advisor=advisor
        self.suggestion=pd.DataFrame(columns=['response','dice lost','relative power','error'],
                                     index=['call liar','call spot on','suggestion:reasonalbe call assumption',
                                            'suggestion: naive call assumption',
                                            'suggestion: simple call assumption','joint suggestion'])
    def bid(self,player_id,rollout,private_dist,ck):
        belief_dist=ck.get_all_common_belief(player_id)
        player_in_game_dice=ck.get_player_in_game_dice(player_id)
#        if len(player_in_game_dice)==2:  #two player game
#            return two_player_game(rollout,ck.las)
            
        if ck.last_bid is None:
            bid_candidate=initial_bid_candidates(rollout,ck.get_total_dice(),self.aggresiveness)
            max_payoff=-1
            response=None 
        else:
            p_liar=private_dist[ck.last_bid[0],ck.last_bid[1]]
            if ck.last_bid[0]>=ck.get_total_dice():
                p_spot_on=p_liar
            else:
                p_spot_on=p_liar-private_dist[ck.last_bid[0]+1,ck.last_bid[1]]
            
                
            if self.simple_minded:
                payoff_call_liar=-p_liar
                payoff_spot_on=p_spot_on-1
            else:
                payoff_call_liar=reward(player_in_game_dice,squared_power,True)*(1-p_liar)+reward(player_in_game_dice,squared_power)*p_liar
                payoff_spot_on=reward(player_in_game_dice,squared_power,True,True)*p_spot_on+reward(player_in_game_dice,squared_power,spot_on=True)*(1-p_spot_on)
            if self.advisor:

                self.suggestion.loc[:2,'dice lost':'relative power']=np.array([[-p_liar,p_spot_on-1],[payoff_call_liar,payoff_spot_on]]).T
            if payoff_call_liar>payoff_spot_on:
                max_payoff=payoff_call_liar
                response=[0]
            else:
                max_payoff=payoff_spot_on
                response=[1]
            bid_candidate=get_bid_candidate(ck.last_bid,private_dist,1/2+self.aggresiveness/2)
        if len(bid_candidate)>0:
            good_response=[]
            good_payoff=np.zeros(3)
            for i in range(3):
                self.response_principle=i
                simulation=Simulation(bid_candidate,rollout,player_in_game_dice,belief_dist,self.response_principle,
                                  self.time_limit,self.judgement,self.bayes_dist,utility_f=self.utility,simple_minded=self.simple_minded)
            
                res,payoff,dice_lost,error=simulation.simulation_result()
                #print(res,payoff,dice_lost,error)
                if self.advisor:
                    self.suggestion.iloc[i+2]=np.array([res,dice_lost,payoff,error])
                #print(res,payoff)
                if payoff>max_payoff:
                    good_response.append(tuple(res))
                    good_payoff[i]=payoff
                else:
                    good_response.append(tuple(response))
                    good_payoff[i]=max_payoff
            response=good_choice(good_response,good_payoff,rollout)
            self.suggestion.iloc[-1]['response']=response
        if self.advisor:
            display(self.suggestion)
        return response





    def reset(self):
        pass
        


