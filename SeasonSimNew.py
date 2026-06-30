import numpy as np

def simulate_game(p,gamesFT=[25,25,15]):
    result=[]
    Ws=[0,0]#calculate score
    for i in gamesFT:
        res=np.random.binomial(2*(i-1),p)
        if res>=i:#win
            result.append([i,2*(i-1)-res])
            Ws[0]+=1
        elif res<i-1:#loss
            result.append([res,i])
            Ws[1]+=1
        else:#draw after first e.g. 24
            if np.random.random()<p**2/(1-2*p+2*p**2):
                result.append([26,24])#for simplicity cap at lenth one
                Ws[0]+=1
            else:
                result.append([24,26])
                Ws[1]+=1
        if Ws[0]>len(gamesFT)//2 or Ws[1]>len(gamesFT)//2:
            break
    return result

#print(simulate_game(0.45))
# for _ in range(500000):
#     simulate_game(np.random.random())