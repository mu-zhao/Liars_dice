import numpy as np 
from probability_calculation import DistributionBelief as DB
from probability_calculation import aggregate_distribution as agg 
dic=['liar','spot-on']  # only for easy read


# def roll_dice(num):
#     """ This is a function simulate dice rolling 
    
#     Arguments:
#         num {int} -- number of dice 
#     Returns:
#         numpy array-- [1,2,0,0,0,0] means the result is 1 one, 2 twos
#     """
#     res=np.zeros(6,dtype=int)
#     for i in np.random.randint(6,size=num):
#         res[i]+=1
#     return res 

def compare(bid,outcome,spot_on=False,trainning=False):
    
    if bid[1]==0:
        if not trainning:
            print('There are %s %ss'%(outcome[bid[1]],bid[1]))
        if spot_on:
            return bid[0]==outcome[0]
        else:
            return bid[0]>outcome[0]
    else:
        if not trainning:
            print('There are %s %ss'%(outcome[int(bid[1])]+outcome[0],bid[1]))
        if spot_on:
            return bid[0]==outcome[0]+outcome[int(bid[1])]
        else:
            return bid[0]>outcome[0]+outcome[int(bid[1])]

def compare_bids(bids):
    if bids[1] is None:
        return False
    w=[0,0]

    for i,b in enumerate(bids):
        if b[1]==0:
            w[i]=b[0]*2
        else:
            w[i]=b[0]
    return w[0]<w[1] or (w[0]==w[1] and bids[0][1]<=bids[1][1])
            
def to_cum_dist(rollout,agg_cum_dist):
    rollout[1:]+=rollout[0]
    res=np.zeros((len(agg_cum_dist)+sum(rollout),6))
    for i in range(6):
        res[rollout[i]:rollout[i]+len(agg_cum_dist),i]=agg_cum_dist[:,i]
        res[rollout[i]+len(agg_cum_dist):,i]=0
    return res 



def validation(bid,last_bid):
    if len(bid)<2:
        if last_bid is None:
            print('You cannot call liar/spot-on in the first round\n')
            return False
        elif bid[0] not in {0,1}:
            print('Invalid bet! \n FYI:0:lair  1:spot-on' )
            return False
        return True
    elif len(bid)>2:
        print('WTF!(read:why the face?)\n Make your bet agian!!!')
        return False
    elif bid[1] not in {0,1,2,3,4,5}:
        print('Denomination out of range\n' )
        return False 
    elif compare_bids([bid,last_bid]):
        print('Your bid %s is not large enough\n'%bid)
        return False
    return True
    
            




class HistoricalProfile:
    pass 


class PlayerPublicProfile:

    def __init__(self,player_id,num_dice,total_dice,call_level,bluff):
        """This is a class of a player's bids
        
        Arguments:
            num_dice {int} -- number of dice this player has
        """
        self.call_level=call_level
        self.bluff=bluff 
        self.id=player_id
        self.dice=num_dice
        self.bids=[]
        self.dist_belief=DB(self.dice,total_dice,call_level,bluff)
        self.history=None 

    def calibrate_bluff(self):
        pass 
    

    def update_belief_about_player(self,last_bid,previous_bid,next_player_call_belief):
        """This is a method to update a player's bids
       
        """
        self.bids.append(last_bid)
        self.dist_belief.bayesian_inference(last_bid,previous_bid,next_player_call_belief)
        self.dist_belief.update_belief_about_player()

    def update_player_belief_about_others(self,players_agg_dist):
        self.dist_belief.update_player_belief_about_others(players_agg_dist)



    def reset(self,player_dice,total_dice): #reset()
        self.dice=player_dice
        self.bids=[]
        self.dist_belief=DB(self.dice,total_dice,self.call_level,self.bluff)
        


class PlayerPrivateProfile:
    """
    """
    def __init__(self,player_id,strategy): 
        self.id=player_id
        self.strategy=strategy
        
    def roll(self,ppp):
        self.roll_result=np.random.choice(ppp.dist_belief.outcome,p=ppp.dist_belief.distribution)
        
    def make_decision(self,common_knowledge,trainning):
        return self.strategy.bid(self.id,self.roll_result,self.private_dist,common_knowledge)
   
    def update(self,ck):
        agg_cum_dist=agg(ck.get_others_agg_dist(self.id))
        self.private_dist=to_cum_dist(self.roll_result,agg_cum_dist)

    def reset(self):
        self.strategy.reset()
        
        
         

class CommonKnowledge:

    def __init__(self,num_dice,num_player,call_level,bluff,start_player_id=0):
        """[summary]
        
        Arguments:
            player_profile {list of PlayerPubicProfile objects} -- public knowledge of each player
            num_players {int} -- total number of players, include those out of game 
            start_player {int} -- first player
        """
        self.dice=num_dice+np.zeros(num_player,dtype=int)
        self.num_players=num_player
        self.first_player=start_player_id 
        self.public_profile=[]
        for i in range(num_player):
            self.public_profile.append(PlayerPublicProfile(i,num_dice,sum(self.dice),call_level,bluff))
        self.whose_turn=start_player_id
        self.turn=0
        self.last_player=None 
        self.last_bid=None 

    def update(self,bid,trainning):
        if not trainning:
            print('Turn %s, Players Dice %s' %(self.turn,self.dice),'Player %s bid %s'%(self.whose_turn,bid))
        for i in range(self.num_players):
            if self.dice[i]>0:
                if i==self.whose_turn:
                    self.public_profile[i].update_belief_about_player(bid,self.last_bid,self.get_next_player_call_belief(i))
                else:
                    self.public_profile[i].update_player_belief_about_others(self.get_others_agg_dist(i))
        self.last_player=self.whose_turn
        self.last_bid=bid 
        self.turn+=1
        while True:
            self.whose_turn=(self.whose_turn+1)%self.num_players
            if self.dice[self.whose_turn]>0:
                break   

    def settle(self,bid,outcome,trainning):
        self.turn=0 
        if bid==[0]:
            if compare(self.last_bid,outcome):   #  successful accusation 
                start_player_id=self.last_player
                if not trainning:
                    print('palyer %s good call, player %s loses one dice'%(self.whose_turn,start_player_id))
                    print('------------------------------------------------------------------')
            else:
                start_player_id=self.whose_turn
                if not trainning:
                    print('player %s bad call, player %s loses one dice'%(start_player_id,start_player_id))
                    print('------------------------------------------------------------------')
            self.dice[start_player_id]-=1
        else:
            start_player_id=self.whose_turn
            if compare(self.last_bid,outcome,True):    #good call 
                self.dice-=np.ones(self.num_players,dtype=int)
                self.dice[start_player_id]+=1        # everyone except the player loses one die 
                if not trainning:
                    print('good call,everyone except player %s loses one dice'%start_player_id)
                    print('------------------------------------------------------------------')
            else:   # not a good call
                self.dice[start_player_id]-=1         # The player loses one die
                if not trainning:
                    print('bad call, player %s loses one dice'%start_player_id)
                    print('------------------------------------------------------------------')
        if self.dice[start_player_id] > 0:      # If the supposed first player still has dice 
            self.whose_turn=start_player_id
        else:
            while self.dice[start_player_id]<1:      # If the suppose first player has no dice, find next player still in game 
                start_player_id=(start_player_id+1)%self.num_players # 
            self.whose_turn=start_player_id
        self.last_player=None 
        self.last_bid=None 
        self.dice[self.dice < 0] = 0
        for i in range(self.num_players):
            if self.dice[i]>0:
                self.public_profile[i].reset(self.dice[i],self.get_total_dice())    # update players' public profile 

    def get_total_dice(self):
        return sum(self.dice)  

    def player_in_game(self):
        return sum(self.dice>0)
    def get_others_agg_dist(self,player_id):    # NOT cumulative dist
        L=[]
        for i in range(self.num_players):
            if self.dice[i]>0 and i!=player_id:
                L.append(self.public_profile[i].dist_belief.agg_info.agg_dist)
        return L 
    def get_all_call_belief(self,player_id):
        L=[]
        for i in range(player_id-self.num_players,player_id):
            if self.dice[i]>0:
                L.append(self.public_profile[i].dist_belief.agg_info.call_dist)
        return L 
        
    def get_player_in_game_dice(self,player_id):
        L=[i if i>0 for i in self.dice[player_id:]]+[i if i>0 for i in self.dice[:player_id]]
        return L 

    def get_next_player_call_belief(self,player_id):
        i=(player_id+1)%self.num_players
        while True:
            if self.dice[i]>0:
                return self.public_profile[i].dist_belief.agg_info.call_dist
            i=(i+1)%self.num_players 
    def get_others_stats(self,player_id):
        expectation=np.zeros(6)
        std=np.zeros(6)
        for i in range(self.num_players):
            if self.dice[i]>0 and i!=player_id:
                expectation+=self.public_profile[i].dist_belief.agg_info.expectation
                std+=self.public_profile[i].dist_belief.agg_info.std
        return expectation,std 
    
class PrivateKnowledge:
    def __init__(self,private_strategies,trainning):
        self.num_private_profile=len(private_strategies)
        self.trainning=trainning
        self.private_profile=[]
        for player_id,strategy in enumerate(private_strategies):
            self.private_profile.append(PlayerPrivateProfile(player_id,strategy))
    def reset(self):
        for private_profile in self.private_profile:
            private_profile.reset()
    def everyone_roll_dice(self,common_knowledge):
        for player,ppp in zip(self.private_profile,common_knowledge.public_profile):
            if ppp.dice>0:
                player.roll(ppp)
                player.update(common_knowledge)


    def everyone_reveal_results(self,common_knowledge):
        s=np.zeros(6,dtype=int)
        for player_id in range(common_knowledge.num_players):
            if common_knowledge.dice[player_id]>0:
                s+=self.private_profile[player_id].roll_result
                if not self.trainning:
                    print('player %s outcome %s'%(player_id,self.private_profile[player_id].roll_result))
        
        if not self.trainning:
            print('total outcome %s' %s)
        return s 

class PlatForm:
    def __init__(self,num_dice,private_strategies,call_level=1/3,bluff=0.1,trainning=False):
        self.num_player=len(private_strategies)
        self.adice=np.zeros(self.num_player)+num_dice
        self.common_knowledge=CommonKnowledge(num_dice,self.num_player,num_dice*self.num_player,call_level,bluff)
        self.private_knowledge=PrivateKnowledge(private_strategies,trainning)
        self.trainning=trainning
        self.new_bid=None  
        self.game_over=False 
    
    def reveal_game(self):
        self.outcome=self.private_knowledge.everyone_reveal_results(self.common_knowledge)
    
    def initialize_game(self):
        self.private_knowledge.everyone_roll_dice(self.common_knowledge)

    def get_valid_bet(self,attempt_allowed=5):
        attempt=0
        while True:    # this loop is just for getting a valid bet
            bid=self.private_knowledge.private_profile[self.common_knowledge.whose_turn].make_decision(self.common_knowledge,self.trainning) 
            if validation(bid,self.common_knowledge.last_bid):      # check is the bid is legit
                self.new_bid=bid 
                return True
            elif attempt>attempt_allowed:
                print('cannot get legit bid from player %s'%self.common_knowledge.whose_turn)
                return False
            attempt+=1
        


    def judge(self):        
        if len(self.new_bid)<2:
            if not self.trainning:
                print('palyer %s call %s'%(self.common_knowledge.whose_turn,dic[self.new_bid[0]]))
            self.reveal_game()
            self.common_knowledge.settle(self.new_bid,self.outcome,self.trainning)
            self.private_knowledge.reset()
            if sum(self.common_knowledge.dice>0)<=1:
                self.game_over=True
            return True   # current round end
        else:
            self.common_knowledge.update(self.new_bid,self.trainning)
            return False # the current round not end
            

    def paly(self): 
        self.initialize_game()
        while True:
            if not self.get_valid_bet(): # if not getting a legit bet
                print('PlatForm: Cannot get valid bet: end game!')
                break 
            if self.judge():  # if current round end
                if self.game_over: # if game is over 
                    print('Game Over')
                    break             
                self.initialize_game() # play a new round 
        return None 
            
                

             





        




        