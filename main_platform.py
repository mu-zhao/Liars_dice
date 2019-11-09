import numpy as np 
from strategies.common import PlatForm as PF 
from strategies.zero_intelligence import ZeroIntelligence as ZI
from strategies.player import HumanPlayer as HP
player=HP()
L=[]
for i in range(1):
    L.append(ZI(np.random.sample(),np.random.random(),np.random.random()))
L.append(player)

Game=PF(5,L)
Game.paly()

    


