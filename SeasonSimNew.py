"""
Executes the simulation
"""
import Simulate
import League
import extract
import EnterData
import SaveData


#Take from html file
#games=extract.extract_data() #you can insert the name of the file here
#Take from existing xlsx file
games=SaveData.load_tournament("SoSe2026Post4")



S=League.Season("SoSe2026",extract.names(games),games)
S.calculate_strength()
print("\n")
print(S.CurTable[["position","points","games won","sets won","sets lost","strength","rallies won","rallies lost"]]) #Table with strengths
print("\n")
#S.save()


# newg=EnterData.enter_games(S.Matchups)
# S.Matchups=newg
# S.calculateTable()
# print(S.CurTable)

################################
#one simulation
#T=S.simulate_rest()
#print(T.CurTable)


#many simulations
#print(Simulate.multi_sim(S,n=1000,showProgress=True,display=True))
#simulations under an assumption
# assumptions1=[
#     [["Wir Sind Helden", "TU Sport II"],[[20,25],[20,25]]],
#     [["TG Sonnenschein", "TU Sport II"],[[20,25],[20,25]]]
#     ] #TU II wins both
# assumptions2=[
#     [["Nusantara", "TU Sport I"],[[20,25],[20,25]]],
#     [["TU Sport I", "Theoretiker"],[[25,20],[25,20]]]
#     ] #TU I wins both
#print(Simulate.multi_sim(S,assumptions=assumptions2,n=500,showProgress=True,display=True))
#L=[[0, 51, 660, 307, 319, 330, 308, 25, 0], [0, 5, 156, 562, 414, 400, 462, 1, 0]] #result out of 2000
#L2 =[[8983, 532, 320, 118, 38, 9, 0, 0, 0], [689, 2215, 1597, 2381, 1719, 1354, 45, 0, 0], [415, 2283, 2733, 1554, 1825, 1190, 0, 0, 0], [386, 451, 821, 2241, 2598, 3477, 26, 0, 0], [189, 3204, 1622, 1689, 1697, 1524, 75, 0, 0], [25, 759, 2786, 2002, 2102, 2325, 1, 0, 0], [0, 0, 0, 5, 20, 103, 6118, 3754, 0], [0, 0, 0, 0, 1, 18, 3735, 6246, 0], [0, 0, 0, 0, 0, 0, 0, 0, 10000]]
#print([[str(j/20)+"%" for j in i] for i in L])