import numpy as np 
#from strategies import probability_calculation
from strategies.common import PlatForm as PF 
from strategies.zero_intelligence import ZeroIntelligence as ZI
from strategies.player import HumanPlayer as HP
from strategies.naive_intelligence import NaiveIntelligence as NI
player=HP()
L=[NI(0.9,5),ZI(0,1),player]
for i in range(2):
    L.append(ZI(np.random.sample(),np.random.random()))


Game=PF(3,L,call_level=1/3,bluff=0.1)
Game.paly()

    


