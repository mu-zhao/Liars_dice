import numpy as np 
import math 
def add_distribution(d1,d2):
    """This function  calculate distribution of two independent random varible. It is convolution (polinomial 
    product rule)
    When d1,d2 have different numbers of columns, d1 has 1 column.
    Arguments:
        d1 {2d array} -- discrete distribution of X
        d2 {2d array} -- discrete distribution of Y
    
    Returns:
        [list] -- distribution of (X+Y)
    """
    d=np.zeros((len(d1)+len(d2)-1,6))
    for i in range(len(d1)):       
        d[i:i+len(d2)]+=d2*d1[i]     #d1 can have the same number of columns as d2 or just has one column.
    return d 

def aggregate_distribution(D):
    """This function takes a list of distribution, returns the aggregate distribution. 
    
    Arguments:
        D {List of array} -- list of individual prob distribution
    
    Returns:
        numpy array -- aggregate distribution
    """
    d=D[0]
    for i in D[1:]:
        if len(i)<len(d):   # run faster
            d=add_distribution(i,d)
        else:
            d=add_distribution(d,i)
    return d 

class AggregateDistribution:
    def __init__(self,agg,n):
        self.expectation=np.zeros(6)+n/3
        self.expectation[0]/=2
        self.std=np.zeros(6)+np.sqrt(2*n)/3
        self.std[0]=np.sqrt(5*n)/6
        self.pure_dist=agg
        self.processed_dist=add_distribution(agg[:,0],agg)
        self.processed_dist[:n+1,0]=agg[:,0]
        self.processed_dist[n+1:,0]=0
        self.cumulative_dist=np.empty_like(self.processed_dist)
        self.cumulative_dist[-1]=self.processed_dist[-1]
        for i in range(2,n+2):
            self.cumulative_dist[-i]=self.cumulative_dist[-i+1]+self.processed_dist[-i]
    

    
class DistributionBelief:
    def __init__(self,n):
        agg=np.zeros((n+1,6))
        prob=np.add.accumulate(np.log(np.arange(1,n+1))) # to calculate distribution 
        index={} 
        outcome=[]
        distribution=[]
        l=[0]*6  #iterator
        for l[0] in range(0,n+1):    
            for l[1] in range(0,n+1-sum(l[:1])): 
                for l[2] in range(0,n-sum(l[:2])):
                    for l[3] in range(0,n+1-sum(l[:3])):
                        for l[4] in range(0,n+1-sum(l[:4])):
                            l[5]=n-sum(l[:5])
                            p=np.exp(prob[6]-sum([prob[i] for i in l])-n*math.log(6))
                            for i in range(6):
                                agg[l[i],i]+=p
                            outcome.append(l)
                            distribution.append(p)
                            index[tuple(l)]=p
        self.index=index
        self.outcome=np.array(outcome)
        self.distribution=np.array(distribution)
        self.agg_dist_info=AggregateDistribution(agg,n)
    
class CommonResponseBelief:
    def __init__(self,dist_player,dist_rest,):
        pass
        
        
        
