import numpy as np 
from strategies.common import PlatForm as PF 
from strategies.zero_intelligence import ZeroIntelligence as ZI
from strategies.player import HumanPlayer as HP
player=HP()
L=[ZI(0.7,0),ZI(0.8,0),ZI(1,0),ZI(0.5,0)]
#for i in range(2):
#    L.append(ZI(np.random.sample(),np.random.random()))
#L.append(ZI(0.8,0))

Game=PF(5,L)
Game.paly()

    


