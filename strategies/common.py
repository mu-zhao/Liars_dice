import numpy as np 


dic=['liar','spot-on']  # only for easy read


def roll_dice(num):
    """ This is a function simulate dice rolling 
    
    Arguments:
        num {int} -- number of dice 
    Returns:
        numpy array-- [1,2,0,0,0,0] means the result is 1 one, 2 twos
    """
    res=np.zeros(6,dtype=int)
    for i in np.random.randint(6,size=num):
        res[i]+=1
    return res 

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

    def __init__(self,player_id,num_dice):
        """This is a class of a player's bids
        
        Arguments:
            num_dice {int} -- number of dice this player has
        """
        
        self.id=player_id
        self.dice=num_dice
        self.bids=[]
        self.distribution_common_belief=
        self.history=None 
    

    def raise_bid(self,bid):
        """This is a method to update a player's bids
        Arguments:
            bid {tuple} -- the bid this player make. (4,5) means 'four fives'. (0,0)
        """
        self.bids.append(bid)




    def update(self,num_dice,num_turn,outcome):
        self.dice=num_dice
        self.bids=[]
        


class PlayerPrivateProfile:
    """
    """
    def __init__(self,player_id,strategy): 
        self.id=player_id
        self.strategy=strategy

    def roll(self,num_dice):
        self.roll_result=roll_dice(num_dice)

    def make_decision(self,common_knowledge,trainning):
        return self.strategy.bid(self.roll_result,common_knowledge)
    
    def reset(self):
        self.strategy.reset()
        
        
         

class CommonKnowledge:

    def __init__(self,num_dice,num_player,start_player_id=0):
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
            self.public_profile.append(PlayerPublicProfile(i,num_dice))
        self.whose_turn=start_player_id
        self.turn=0
        self.last_player=None 
        self.last_bid=None 

    def update(self,bid,trainning):
        if not trainning:
            print('Turn %s, Players Dice %s' %(self.turn,self.dice),'Player %s bid %s'%(self.whose_turn,bid))
        self.public_profile[self.whose_turn].raise_bid(bid)
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
                self.public_profile[i].update(self.dice[i],self.turn,outcome)     # update players' public profile 

    def get_total_dice(self):
        return sum(self.dice)  

    def player_in_game(self):
        return sum(self.dice>0)

            
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
        for player,dice in zip(self.private_profile,common_knowledge.dice):
            if dice>0:
                player.roll(dice)


    def eeveryone_reveal_results(self,common_knowledge):
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
    def __init__(self,num_dice,private_strategies,trainning=False):
        self.common_knowledge=CommonKnowledge(num_dice,len(private_strategies))
        self.private_knowledge=PrivateKnowledge(private_strategies,trainning)
        self.trainning=trainning
        self.new_bid=None  
        self.game_over=False 
    
    def reveal_game(self):
        self.outcome=self.private_knowledge.eeveryone_reveal_results(self.common_knowledge)
    
    def initialize_game(self):
        self.private_knowledge.everyone_roll_dice(self.common_knowledge)

    def get_valid_bet(self,attempt_allowed=3):
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
            
                

             





        




        