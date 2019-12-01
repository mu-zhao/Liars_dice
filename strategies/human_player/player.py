import numpy as np 

class HumanPlayer:
    def __init__(self,console=False,advisor=None):
        self.console=console
        self.advisor=advisor
    def bid(self,player_id,dice_result,private_dist,common_knowledge):
        print('current players in game dice:',common_knowledge.dice)
        if self.advisor is None:
            print('Your dice result%s'%dice_result)
        while True:
            try:
                bid=list(map(int,str(input('Player%s, Your bid?\n'%player_id)).strip(' ').split(',')))
                break
            except ValueError:
                print('Input has to be 0 or 1 or a pair of integers')
        return bid 
    def reset(self):
        print('A new round of game')