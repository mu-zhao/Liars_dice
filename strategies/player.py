import numpy as np 

class HumanPlayer:
    def __init__(self,console=False):
        self.console=console
    def bid(self,player_id,dice_result,private_dist,common_knowledge):
        print('current players dice%s, Your dice result%s'%(common_knowledge.dice,dice_result))
        while True:
            try:
                bid=list(map(int,str(input('Your bid\n')).strip(' ').split(',')))
                break
            except ValueError:
                print('Input has to be 0 or 1 or a pair of integers')
        return bid 
    def reset(self):
        print('A new round of game')