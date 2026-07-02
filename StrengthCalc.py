import numpy as np

def vec2simplexM1(vecX, l=1.):#projection algorithm by Christian Bauckhage - ResearchGate
    m = vecX.size

    vecS = np.sort(vecX)[::-1]
    vecC = np.cumsum(vecS) - l
    vecH = vecS - vecC / (np.arange(m) + 1)

    r = np.max(np.where(vecH>0)[0])
    t = vecC[r] / (r + 1)

    return np.maximum(0, vecX - t)

def vec2simplexM2(vecX, l=1.,eps=0.0001):#just clip and normalize
    vecN= np.maximum(eps, vecX)#to avoid division by 0
    if sum(vecN)==0:
        print("Cannot project vector")
        return 0
    return l*vecN/sum(vecN)

#a bit unnecessary, "simpler" case for gradient
def dlogPds1(result,s1,s2):#result is a list with the different sets
    # Probability for one match e.g. k-25: (24+k Choose k) p^k(1-p)^(24+k-k)*(1-p)
    # -> log -> p = s1/(s1+s2) -> derivative of log( (24+k Choose k) (s1/(s1+s2))^k(s2/(s1+s2))^25 )= 
    # log( (24+k Choose k) (s1^k*s2^25)/(s1+s2)^(25+k))
    # (24+k Choose k)*((k*s1^(k-1)*s2^25)(s1+s2)^(25+k)-(s1^k*s2^25)(25+k)(s1+s2)^(24+k)/(s1+s2)^(2*(25+k))*((24+k Choose k) (s1^k*s2^25)/(s1+s2)^(25+k))^-1
    # =(k(s1+s2)-s1(25+k))/(s1+s2)*(s1)^-1 = (k(1+s2/s1)-(25+k))/(s1+s2) = (s2/s1*k-25)/(s1+s2)
    # simpler by applying log laws directly to quotient and then derivating
    ds1=0
    for satz in result:
        if satz[0]>satz[1]:
            ds1+=(satz[0]*s1/s2-satz[1])/(s1+s2)
        else:
            ds1+=(satz[0]-satz[1]*s1/s2)/(s1+s2)
    return ds1

def Pgradient(games,s,namedict={},namelist=[]):
    """
    Args:
        games (list): List of games where every game is a list consisting of the two teamnames and a list of all sets they played
        s (np.array): strength parameters corresponding to the teams, for positions see namedict
        namedict (dict): gives the number/position in s to every teamname, 0-indexed!
    """
    if not namelist and namedict:#so we can also get the name corresponding to a number
        namelist= len(namedict)*[""]
        for key,val in namedict.items():
            namelist[key]=val
    elif namelist and not namedict:
        namedict={t:i for i,t in enumerate(namelist)}
    elif namelist and namedict:
        pass
    else:
        raise LookupError("No way to associate strenghts with teams")

    grad=np.zeros(len(s)) #initialize gradien´t
    
    for g in games:
        t1=namedict[g[0][0]] #positions of the two teams involved
        t2=namedict[g[0][1]]
        s1=s[t1]
        s2=s[t2]
        for satz in g[1]:#for logic, see dlogPds1
            if satz[0]>satz[1]:
                change=(satz[0]*s2/s1-satz[1])/(s1+s2)
            else:
                change=(satz[0]-satz[1]*s1/s2)/(s1+s2)
            grad[t1]+=change
            grad[t2]-=change

    return grad

def gradPdescent(games,sPrior,namedict={},namelist=[],l=1e-5,n=10000):
    sNew=np.copy(sPrior)
    simp_size=len(sNew)#was accidentally also called l
    eps=0.001#Abbruch
    for _ in range(n):
        grad=Pgradient(games,sNew,namedict=namedict,namelist=namelist)
        if np.sum(grad**2)<eps:
            break
        sNew+=l*grad
        sNew=vec2simplexM2(sNew,l=simp_size)
        #print(sNew)
    return sNew
    

"""
def Test():
    games=extract_data()
    Teams=[]
    for i in games:
        for t in i[0]:
            if not t in Teams:
                Teams.append(t)
    #print(Pgradient(games,np.ones(9),namelist=Teams),Teams)
    print(gradPdescent(games,np.ones(9),namelist=Teams),Teams)

Test()
#Pgradient(extract_data(),np.ones(9),)
"""