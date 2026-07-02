import pandas as pd
import numpy as np
import copy

import Simulate
import StrengthCalc


class Season():
    def __init__(self,Name,Teams: list[str],Matchups: list,CurTable: pd.DataFrame=pd.DataFrame([])):
        self.Name=Name
        self.Teams=Teams
        self.Matchups=Matchups
        self.CurTable=CurTable
        if not len(CurTable.index):
            self.CurTable=self.calculateTable()
    def calculateTable(self): #option to only update but should be reasonably fast as is
        if not len(self.CurTable.index):
            Table=pd.DataFrame({"points":[0 for i in self.Teams],"position":[0 for i in self.Teams],
                                    "games":[0 for i in self.Teams],"setdiff":[0 for i in self.Teams],"sets won":[0 for i in self.Teams],
                                    "sets lost":[0 for i in self.Teams]},
                                index=[i for i in self.Teams])
        else:
            Table=pd.DataFrame({"points":[0 for i in self.Teams],"position":[0 for i in self.Teams],
                                    "games":[0 for i in self.Teams],"setdiff":[0 for i in self.Teams],"sets won":[0 for i in self.Teams],
                                    "sets lost":[0 for i in self.Teams]},
                                index=[i for i in self.Teams])
            Table=pd.concat([self.CurTable,Table])
            Table=Table.groupby(level=0).last()
        #self.CurTable.loc[["points","position","games","setdiff","sets won","sets lost"]]

        for M in self.Matchups:
            T=M[0]
            R=M[1]
            p1,p2=points(R)
            #print(p1,p2)
            if R: #update all the conditional stuff
                Table.loc[T[0],"games"]+=1
                Table.loc[T[1],"games"]+=1
                if p1==0:
                    Table.loc[T[0],"setdiff"]-=2
                    Table.loc[T[0],"sets lost"]+=2
                    Table.loc[T[1],"setdiff"]+=2
                    Table.loc[T[1],"sets won"]+=2
                elif p1==1:
                    Table.loc[T[0],"setdiff"]-=1
                    Table.loc[T[0],"sets lost"]+=2
                    Table.loc[T[0],"sets won"]+=1
                    Table.loc[T[1],"setdiff"]+=1
                    Table.loc[T[1],"sets lost"]+=1
                    Table.loc[T[1],"sets won"]+=2
                elif p2==1:
                    Table.loc[T[1],"setdiff"]-=1
                    Table.loc[T[1],"sets lost"]+=2
                    Table.loc[T[1],"sets won"]+=1
                    Table.loc[T[0],"setdiff"]+=1
                    Table.loc[T[0],"sets lost"]+=1
                    Table.loc[T[0],"sets won"]+=2
                elif p2==0:
                    Table.loc[T[1],"setdiff"]-=2
                    Table.loc[T[1],"sets lost"]+=2
                    Table.loc[T[0],"setdiff"]+=2
                    Table.loc[T[0],"sets won"]+=2
            Table.loc[T[0],"points"]+=p1
            Table.loc[T[1],"points"]+=p2
        Table.sort_values(by=["points","setdiff"],inplace=True,key=lambda x:-x) #sort
        curpoints=Table.iloc[0]["points"]
        curdiff=Table.iloc[0]["setdiff"]
        curpos=1
        for i,y in enumerate(Table.index):#calculate positions
            if Table.loc[y,"points"]==curpoints and Table.loc[y,"setdiff"]==curdiff:
                Table.loc[y,"position"]=curpos
            else:
                curpoints=Table.loc[y,"points"]
                Table.loc[y,"position"]=i+1#0 ndexed
                curpos=i+1
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
                
        


#Point assignment
def points(Results):
    if not Results:
        return 0,0
    T1Wins=sum([1 for i in Results if i[0]>i[1]])
    T2Wins=sum([1 for i in Results if i[0]<i[1]])
    T1Points=T1Wins if T1Wins<2 else (2 if T2Wins==1 else 3)
    return T1Points,3-T1Points