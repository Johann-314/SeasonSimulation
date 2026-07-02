import Simulate
import League
import extract

games=extract.extract_data() #you can insert the name of the file here
S=League.Season("SoSe2026",extract.names(games),games)
S.calculate_strength()
print(S.CurTable)
T=S.simulate_rest()
print(T.CurTable)
#print(S.CurTable)
#print(Simulate.multi_sim(S,["TU Sport I","TU Sport II"],n=2000,showProgress=True))
L=[[0, 51, 660, 307, 319, 330, 308, 25, 0], [0, 5, 156, 562, 414, 400, 462, 1, 0]] #result out of 2000
print([[str(j/20)+"%" for j in i] for i in L])