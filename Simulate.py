import numpy as np
import League

def random_round(x):#for more realistic rounding
    base=x//1
    #print(base,x-base)
    return int(base+(np.random.random() < x-base))

def simulate_game(p,gamesFT=[25,25,15]):
    result=[]
    Ws=[0,0]#calculate score
    for i in gamesFT:
        res=np.random.binomial(2*(i-1),p) #generate e.g. first 48 points
        k=min(res,2*(i-1)-res) #losers score
        x=random_round(i*k/(2*(i-1)-k)) #so that portion of rounds won before end is roughly the same as in res
        if res>=i:#win
            result.append([i,x])
            Ws[0]+=1
        elif res<i-1:#loss
            result.append([x,i])
            Ws[1]+=1
        else:#draw after first e.g. 24
            if np.random.random()<p**2/(1-2*p+2*p**2): #Markov chain calculation for win_probability
                result.append([i+1,i-1])#for simplicity cap at lenth one
                Ws[0]+=1
            else:
                result.append([i-1,i+1])
                Ws[1]+=1
        if Ws[0]>len(gamesFT)//2 or Ws[1]>len(gamesFT)//2:
            break
    return result

def multi_sim(S,interesting,assumptions=[],n=10,showProgress=False):
    Places=[len(S.Teams)*[0] for t in interesting]
    S.calculate_strength()
    if showProgress:
        displayEvery = n//200 +1 #every so and so much should be updated
    for i in range(n):
        if showProgress and i%displayEvery==0:
            print(str(round(100*i/n))+"%")
        T=S.simulate_rest()
        for i in range(len(interesting)):
            Places[i][T.CurTable.loc[interesting[i],"position"]]+=1
    return Places
        