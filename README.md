# Liars_dice

This project
1. creates an extensible platform to play the game liar's dice; 
2. creates multiple AIs to play liar's dice;
3. creates AI advisors to help player play the game;

Files:


1.**main_platfrom.py**:

 the main platform to play the game


2.**common.py**:

 supporting file of the platform



3.**lairs_dice advisor.ipynb**:

 showcase of use one(or several) of the AIs to play as advisor to the player.

4.**liars_dice AIs.ipynb**:
 
 showcase of play by various AIs

5.**liars_dice AIs vs human.ipynb**:

showcase of human play with AIs


6.**strategies**:

various AIs that play liar's dice.

## For more details on the AIs, please go to [**AIs for Liar's dice**](https://github.com/mu-zhao/Liars_dice/wiki/Zero-Intelligence)
-----------------------------------
## Template for your own bot!!!
   
   ``` Python 3
   class YourBot:
    def __init__(self,**arg):
        pass
    def preprocess(self,dice_result,ck): #ck is class CommonKnowledge
        pass 
    def reset(self):
        pass
    def update_goodbet(self,bid):
        pass
    def bid(self,player_id,dice_result,private_dist,ck):# private_dist is the distribution belief about others
        pass 
   ```
   


To read math format on Github, you might need [_MathJax Plugin for Github_]( https://chrome.google.com/webstore/detail/mathjax-plugin-for-github/ioemnmodlmafdkllaclgeombjnmnbima)
