import numpy as np
from strategies.common import PlatForm as PF 
from strategies.epsilon_intelligence import EpsilonIntelligence as EI
from strategies.zero_intelligence import ZeroIntelligence as ZI
from strategies.player import HumanPlayer as HP
from strategies.naive_intelligence import NaiveIntelligence as NI
player=HP()

x=[]
for i in range(160):
    L=[]
#    L=[NI(simulation_time_limit=0.5,aggresive=0.9,simple_minded=False,response_principle=0)]
    for i in range(3):
        L.append(ZI(np.random.sample(),np.random.sample(),np.random.sample()))
    Game=PF(5,L,call_level=1/3,bluff=0.05,trainning=True)
    x.append(Game.play())

#Game=PF(5,L,call_level=1/3,bluff=0.05,advisor=1,savage_settle=False,trainning=True)
#Game.play()

    



