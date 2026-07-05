import pandas as pd
import numpy as np
import copy

import Simulate
import StrengthCalc
import SaveData


class Season():
    def __init__(self,Name,Teams: list[str],Matchups: list,CurTable: pd.DataFrame=pd.DataFrame([])):
        self.Name=Name
        self.Teams=Teams
        self.Matchups=Matchups
        self.CurTable=CurTable
        if not len(CurTable.index):
            self.calculateTable()
    def calculateTable(self): #option to only update but should be reasonably fast as is
        Table=pd.DataFrame({"points":[0 for i in self.Teams],"position":[0 for i in self.Teams],
                                    "games":[0 for i in self.Teams],"sets won":[0 for i in self.Teams],
                                    "sets lost":[0 for i in self.Teams],"rallies won":[0 for i in self.Teams],
                                    "rallies lost":[0 for i in self.Teams]},
                                index=[i for i in self.Teams])
        if len(self.CurTable.index):
            Table=pd.concat([self.CurTable,Table])
            Table=Table.groupby(level=0).last()
        #self.CurTable.loc[["points","position","games","setdiff","sets won","sets lost"]]
        for M in self.Matchups:
            T=M[0]
            R=M[1]
            if R: #update all the stuff
                rallies=[sum([r[j] for r in R]) for j in range(2)]
                sets=[sum([r[j]>r[1-j] for r in R]) for j in range(2)]#unneccesarily compact :)
                for i in range(2): #1-i is the other index
                    Table.loc[T[i],"games"]+=1
                    Table.loc[T[i],"sets won"]+=sets[i]
                    Table.loc[T[i],"sets lost"]+=sets[1-i]
                    Table.loc[T[i],"rallies won"]+=rallies[i]
                    Table.loc[T[i],"rallies lost"]+=rallies[1-i]
                    Table.loc[T[i],"points"]+=sets[i]+(sets[1-i]==0)
        Table["setdiff"]=Table["sets won"]-Table["sets lost"]
        Table["setquot"]=(Table["sets won"]/Table["sets lost"]).where(Table["sets lost"] != 0, float("inf"))
        Table["raldiff"]=Table["rallies won"]-Table["rallies lost"]
        Table["ralquot"]=(Table["rallies won"]/Table["rallies lost"]).where(Table["rallies lost"] != 0, float("inf"))
        #sorting and position determining
        characteristics=["points","setdiff","setquot","raldiff","ralquot"] #sorting criteria
        Table.sort_values(by=characteristics,inplace=True,key=lambda x:-x) #sort
        diff = Table[characteristics].ne(Table[characteristics].shift()).any(axis=1) # True where row differs from previous row
        group_id = diff.cumsum() # Group ID for identical blocks
        block_sizes = Table.groupby(group_id).size() # Size of each block
        Table["position"] = group_id.map(block_sizes.cumsum()) # Position = cumulative sum of block sizes up to this block
        self.CurTable=Table
        return Table
    def calculate_strength(self):
        s=StrengthCalc.gradPdescent(self.Matchups,np.ones(len(self.Teams)),namelist=list(self.CurTable.index))
        if "strength" in self.CurTable.keys():
            self.CurTable["strength"]=s
        else:
            self.CurTable.insert(4,"strength",s)
    def simulate_rest(self,assumptions=[]):
        TempSeason=Season(self.Name+"Tmp",self.Teams,copy.deepcopy(self.Matchups),self.CurTable.copy()) #potential problems without copy
        try:#ensure that strength was calculated
            TempSeason.CurTable["strength"]
        except:
            TempSeason.calculate_strength()
        for g in assumptions:
            try:
                i=TempSeason.Matchups.index([g[0],[]])
            except ValueError:
                raise ValueError("Invalid assumption")
            TempSeason.Matchups[i]=g
        for g in TempSeason.Matchups:
            if not g[1]:
                s1=TempSeason.CurTable.loc[g[0][0],"strength"]
                s2=TempSeason.CurTable.loc[g[0][1],"strength"]
                g[1]=Simulate.simulate_game(s1/(s1+s2))
        TempSeason.CurTable=TempSeason.calculateTable()
        return TempSeason
    def save(self):
        SaveData.update_history(self.Matchups,self.Name)
        


#Point assignment
def points(Results):
    if not Results:
        return 0,0
    T1Wins=sum([1 for i in Results if i[0]>i[1]])
    T2Wins=sum([1 for i in Results if i[0]<i[1]])
    T1Points=T1Wins if T1Wins<2 else (2 if T2Wins==1 else 3)
    return T1Points,3-T1Points