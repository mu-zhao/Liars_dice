import numpy as np
from strategies.common import PlatForm as PF 
from strategies.epsilon_intelligence import EpsilonIntelligence as EI
from strategies.zero_intelligence import ZeroIntelligence as ZI
from strategies.player import HumanPlayer as HP
from strategies.naive_intelligence import NaiveIntelligence as NI
player=HP()
L=[NI(simulation_time_limit=0.1,aggresive=0.9,simple_minded=False,response_principle=0)]
for i in range(3):
    L.append(player)

#L=[NI(simulation_time_limit=0.5,aggresive=0.9,simple_minded=False,response_principle=0)]
#L+=L
#L+=L

#Game=PF(5,L,call_level=1/3,bluff=0.05,trainning=False)

Game=PF(5,L,call_level=1/3,bluff=0.05,advisor=0,savage_settle=True,trainning=False)
Game.play()

    



