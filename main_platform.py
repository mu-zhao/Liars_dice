import numpy as np 
#from strategies import probability_calculation
from strategies.common import PlatForm as PF 
from strategies.epsilon_intelligence import EpsilonIntelligence as EI
from strategies.zero_intelligence import ZeroIntelligence as ZI
from strategies.player import HumanPlayer as HP
from strategies.naive_intelligence import NaiveIntelligence as NI
player=HP()
L=[]
#L=[NI(0.8,1,response_principle=0,blur=False),ZI(0.5,0.5)]

#for i in range(3):
#    L.append(ZI(np.random.sample(),np.random.sample(),np.random.sample()))
for i in range(1):
    L.append(player)
#L+=[player]
L+=[NI(simulation_time_limit=0.01,aggresive=0.9,simple_minded=False,response_principle=0)]
x=[]
#for i in range(30):
#    Game=PF(5,L,call_level=1/3,bluff=0.05,trainning=True)
#    x.append(Game.paly())

Game=PF(5,L,call_level=1/3,bluff=0.05,advisor=1,savage_settle=True,trainning=False)
Game.first_advisor()

    



