import pandas as pd
import numpy as np

class Team():
    def __init__(self,Name: str):
        self.Name=Name

class Matchup():#only allows for whole matchup or nothing
    def __init__(self,Team1: Team,Team2: Team,Result: list[tuple]|None=None):
        self.Team1=Team1
        self.Team2=Team2
        self.Result=Result
    def get_points(self,team: Team):#TU-Volleyball specific
        T1Wins=sum([1 for i in self.Result if i[0]>i[1]])
        T2Wins=sum([1 for i in self.Result if i[0]<i[1]])
        T1Points=T1Wins if T1Wins<2 else (2 if T2Wins==1 else 3)
        if team==self.Team1:
            return T1Points
        elif team==self.Team2:
            return 3-T1Points



class Season():
    def __init__(self,Name,Teams: list[Team],Matchups: list[Matchup],CurTable: pd.DataFrame=pd.DataFrame([])):
        self.Name=Name
        self.Teams=Teams
        self.Matchups=Matchups
        self.CurTable=CurTable
        self.calculateTable()
    def calculateTable(self,Games=None,type="Whitelist",reset=True):
        if reset:
            Table=pd.DataFrame({"points":[0 for i in self.Teams],"position":[0 for i in self.Teams]},
                               index=[i.Name for i in self.Teams])#erstmal mit .Name
        else:
            Table=self.CurTable
        if Games==None:
            considerGames=[i for i in self.Matchups if i.Result!=None]
        elif type=="Blacklist":
            considerGames=[i for i in self.Matchups if i not in Games]
        else:
            considerGames=Games.copy()
        for G in considerGames:
            Table[G.Team1.Name]["points"]+=G.get_points(G.Team1)
            Table[G.Team2.Name]["points"]+=G.get_points(G.Team2)
        Table.sort_values("points",inplace=True)
        curpoints=Table.iloc[0]["points"]
        curpos=1
        for i in len(Table):
            if Table.iloc[i]["points"]==curpoints:
                Table.iloc["position"]=curpos
            else:
                curpoints=Table.iloc[i]["points"]
                Table.iloc["position"]=i
                curpos=i
        return Table
                
def VBLigaWS2526():
    TeamNames=["BCV","GUS","Los Pankos","Who Knows","Theoretiker","TG Sonnenschein",
            "Eintracht Südring","TU Sport I","TU Sport II"]
    Teams=[Team(i) for i in TeamNames]

def Test():
    d=pd.DataFrame({"points":[2,3,2,1],"position":[0,0,1,0]},index=["A","B","C","D"])
    d.iloc[0]["points"]=20
    print(d.iloc[0]["points"],len(d))
    d.sort_values(by=["points","position"],inplace=True)

Test()