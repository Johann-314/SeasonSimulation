import pandas as pd
import numpy as np
import copy

# class Team():
#     def __init__(self,Name: str):
#         self.Name=Name

# class Matchup():#only allows for whole matchup or nothing
#     def __init__(self,Team1: Team,Team2: Team,Result: list[tuple]|None=None):
#         self.Team1=Team1
#         self.Team2=Team2
#         self.Result=Result
#     def get_points(self,team: Team):#TU-Volleyball specific
#         T1Wins=sum([1 for i in self.Result if i[0]>i[1]])
#         T2Wins=sum([1 for i in self.Result if i[0]<i[1]])
#         T1Points=T1Wins if T1Wins<2 else (2 if T2Wins==1 else 3)
#         if team==self.Team1:
#             return T1Points
#         elif team==self.Team2:
#             return 3-T1Points

def points(TeamNames,Results,special=True):
    if not Results:
        return 0,0
    if special:
        if TeamNames[0]=="GUS":
            return (0,3)
        elif TeamNames[1]=="GUS":
            return (3,0)
    T1Wins=sum([1 for i in Results if i[0]>i[1]])
    T2Wins=sum([1 for i in Results if i[0]<i[1]])
    T1Points=T1Wins if T1Wins<2 else (2 if T2Wins==1 else 3)
    return T1Points,3-T1Points


class Season():
    def __init__(self,Name,Teams: list[str],Matchups: dir,CurTable: pd.DataFrame=pd.DataFrame([])):
        self.Name=Name
        self.Teams=Teams
        self.Matchups=Matchups
        self.CurTable=CurTable
        self.CurTable=self.calculateTable(updateStrength=True)
    def calculateTable(self,Games=None,type="Whitelist",reset=True,updateStrength=False):
        if reset:
            Table=pd.DataFrame({"points":[0 for i in self.Teams],"position":[0 for i in self.Teams],
                                "games":[0 for i in self.Teams],"setdiff":[0 for i in self.Teams]},
                               index=[i for i in self.Teams])
        else:
            Table=self.CurTable
        if Games==None:
            considerGames={i:self.Matchups[i] for i in self.Matchups.keys() if self.Matchups[i]!=None}
        elif type=="Blacklist":
            considerGames={i:self.Matchups[i] for i in self.Matchups.keys() if i not in Games.keys()}
        else:
            considerGames=Games
        for T,R in considerGames.items():
            p1,p2=points(T,R)
            #print(p1,p2)
            if R:
                Table.loc[T[0],"games"]+=1
                Table.loc[T[1],"games"]+=1
                if p1==0:
                    Table.loc[T[0],"setdiff"]-=2
                    Table.loc[T[1],"setdiff"]+=2
                elif p1==1:
                    Table.loc[T[0],"setdiff"]-=1
                    Table.loc[T[1],"setdiff"]+=1
                elif p2==1:
                    Table.loc[T[0],"setdiff"]+=1
                    Table.loc[T[1],"setdiff"]-=1
                elif p2==0:
                    Table.loc[T[0],"setdiff"]+=2
                    Table.loc[T[1],"setdiff"]-=2
            Table.loc[T[0],"points"]+=p1
            Table.loc[T[1],"points"]+=p2
        Table.sort_values(by=["points","setdiff"],inplace=True,key=lambda x:-x)
        curpoints=Table.iloc[0]["points"]
        curdiff=Table.iloc[0]["setdiff"]
        curpos=1
        for i,y in enumerate(Table.index):
            if Table.loc[y,"points"]==curpoints and Table.loc[y,"setdiff"]==curdiff:
                Table.loc[y,"position"]=curpos
            else:
                curpoints=Table.loc[y,"points"]
                Table.loc[y,"position"]=i+1#0 ndexed
                curpos=i+1
        if updateStrength:
            Table.insert(4,"strength",[1 for _ in self.Teams])
            for _ in range(50):
                old_Table=copy.deepcopy(Table)
                for T,R in considerGames.items():
                    p1,p2=points(T,R,special=False)
                    Table.loc[T[0],"strength"]+=p1*old_Table.loc[T[1],"strength"]/old_Table.loc[T[0],"games"]
                    Table.loc[T[1],"strength"]+=p2*old_Table.loc[T[0],"strength"]/old_Table.loc[T[1],"games"]
                Table["strength"]=len(self.Teams)*Table["strength"]/sum(Table["strength"])
            
        # for i in range(len(Table)):
        #     if Table.iloc[i]["points"]==curpoints:
        #         Table.iloc[i]["position"]=curpos
        #     else:
        #         curpoints=Table.iloc[i]["points"]
        #         Table.iloc[i,"position"]=i
        #         curpos=i
        return Table
    def brute_rest_simulation(self):
        left=[]
        for T,R in self.Matchups.items():
            if not R:
                left.append(T)
        n=len(left)
        if n==0:
            return [self.calculateTable()]
        standings=[]
        possible_Results=[[(25,0),(25,0)],[(0,25),(0,25)]]#,[(25,0),(0,25),(15,0)]][(0,25),(0,25)],[(25,0),(0,25),(0,15)]]
        k=len(possible_Results)
        # for i in range(k**n):
        #     S_alt=self.copy()
        for R in possible_Results:
            S_alt=copy.deepcopy(self)
            S_alt.Matchups[left[0]]=R
            standings=standings + S_alt.brute_rest_simulation()
        return standings
    
    def strength_based_game_sim(self,Matches=[],assumptions={}):
        S_alt=copy.deepcopy(self)
        for k in assumptions:
            S_alt.Matchups[k]=assumptions[k]
        if not Matches:
            for T,R in S_alt.Matchups.items():
                if not R:
                    Matches.append(T)
        #print(("Theoretiker","TU Sport I") in Matches)
        for T in Matches:
            s1,s2=self.CurTable.loc[T[0],"strength"],self.CurTable.loc[T[1],"strength"]
            G1=(25,0) if np.random.random()<s1/(s1+s2) else (0,25)
            G2=(25,0) if np.random.random()<s1/(s1+s2) else (0,25)
            if G1!=G2:
                G3=(25,0) if np.random.random()<s1/(s1+s2) else (0,15)
                S_alt.Matchups[T]=[G1,G2,G3]
            else:
                S_alt.Matchups[T]=[G1,G2]
        return S_alt.calculateTable(updateStrength=False)
    def possible_range(self,Team):#not completed
        print("Not done yet")
        left_others=[]
        left_own=[]
        for T,R in self.Matchups.items():
            if not R:
                if Team in T:
                    left_own.append(T)
                else:
                    left_others.append(T)
        possible_Results=[[(25,0),(25,0)],[(0,25),(0,25)],[(25,0),(0,25),(15,0)],[(0,25),(0,25)],[(25,0),(0,25),(0,15)]]
        #best in place 0, worst in 1st place
        S_alt=copy.deepcopy(self)
        start_pos=self.CurTable[Team]
        for G in left_own:
            if G[0]==Team:
                S_alt.Matchups[G]=possible_Results[0]
            else:
                S_alt.Matchups[G]=possible_Results[1]
                
def VBLigaWS2526():
    Teams=[("BCV","BCV"),("GUS","GUS"),("Los Pankows","Los"),("Who Knows","Who"),("Theoretiker","Theo"),
           ("TG Sonnenschein","TG"),("Eintracht Südring","ES"),("TU Sport I","TUI"),("TU Sport II","TUII")]
    #Matchups={(Teams[i][1],Teams[j][1]) for i in range(len(Teams)) for j in range(i)}
    #Spieltag1=[["BCV","GUS","LP"],["Who","Theo","TG"]]
    #Get data
    fields=[("<div class=\"table-cell team_name_inner\">","</div>"),
            ("<span class=\"result_gt\">","</span>"),("<span class=\"result_lt\">","</span>"),
            ]
    status=0
    Games={}
    with open("LigaDaten2526.txt","r",errors="ignore") as f:
        for line in f:
            for i,field in enumerate(fields):
                if field[0] in line:
                    #problem because both in same line
                    start,end=field
                    tn=line.split(start, 1)[1].split(end, 1)[0]
                    if i==0:
                        tn=tn.replace("Ã¼","ü")
                        tn=tn.replace("&shy;","")
                        if status==0:
                            status=1
                            curTeam1=tn
                        elif status==1:
                            status=0
                            curTeam2=tn
                            Games[(curTeam1,curTeam2)]=[]
                    elif i==1 or i==2:
                        #very weird special case, whatever happened here:
                        if i==1 and tn=="0":
                            print("Weird Game detected")
                            status=0
                            Games[(curTeam1,curTeam2)].append((15,0))
                        elif status==0:
                            status=1
                            score1=tn
                            if len(line.split(start, 1)[0])<len(line.split(start, 1)[1]):
                                pos=0
                            else:
                                pos=1
                        elif status==1:
                            status=0
                            if pos==0:
                                Games[(curTeam1,curTeam2)].append((int(score1),int(tn)))
                            else:
                                Games[(curTeam1,curTeam2)].append((int(tn),int(score1)))
                    #print(tn)
    #print(Games)
    Games[("TG Sonnenschein","TU Sport I")]=[(0,25),(25,0),(0,15)]#not actual result
    Games[("TG Sonnenschein","GUS")]=[(25,0),(0,25),(15,0)]#Result doesn't matter appearantly
    S=Season("2526",[i[0] for i in Teams],Games)
    #S_=S.copy()
    print(S.CurTable)
    #print([i for i in S.CurTable])
    #print(S.strength_based_game_sim())
    #print(S.Matchups)
    interesting_Teams=["TU Sport I","TU Sport II"]
    end_positions=[{} for _ in interesting_Teams]
    strengthsim=1000
    a1={("Theoretiker","TU Sport I"):[(0,25),(0,25)],("Los Pankows","TU Sport I"):[(0,25),(0,25)]}
    for k in range(strengthsim):
        Table=S.strength_based_game_sim(assumptions=a1)
        #print(Table)
        for i,T in enumerate(interesting_Teams):
            p=Table.loc[T,"position"]
            if p not in end_positions[i]:
                end_positions[i][p]=1
            else:
                end_positions[i][p]+=1
    print(end_positions)
    brute=False
    if brute:
        standings=(S.brute_rest_simulation())#somehow wrong
        print(standings[0])
        places={}
        for s in standings:
            place=s.loc["TU Sport I","position"]
            if place in places:
                places[place]+=1
            else:
                places[place]=1
        print(places)

VBLigaWS2526()


def Test():
    d=pd.DataFrame({"points":[2,3,2,1],"position":[0,0,1,0]},index=["A","B","C","D"])
    #d.loc[0,"points"]=int(20)
    #print(d.loc[0,"points"],len(d))
    print(d)
    print([x for x in d.index])
    d.insert(2,"strength",[2,3,4,5])
    d.sort_values(by=["points","position"],inplace=True)
    print(d["position"]/sum(d["points"]))


#Test()