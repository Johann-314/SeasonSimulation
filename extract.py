

def extract_data(name="Random\SeasonSimulation\LigaDaten26.txt"):
    with open(name,"r",errors="ignore") as f:
        Games=[]
        fields=[("<div class=\"table-cell team_name_inner\">","</div>"),
            ("<span class=\"result_gt\">","</span>"),("<span class=\"result_lt\">","</span>"),
            ]#interesting parts, (start,end)
        openGame=False #just to know where we are in the parsing
        openSet=False
        for line in f:
            for i,field in enumerate(fields):
                if field[0] in line:
                    #problem because both in same line
                    start,end=field
                    tn=line.split(start, 1)[1].split(end, 1)[0]#extract relevant part, i.e. Teamname/score
                    if i==0:
                        tn=tn.replace("Ã¼","ü")#handle special characters
                        tn=tn.replace("&shy;","")
                        if not openGame:
                            openGame=True
                            curTeam1=tn
                        elif openGame:
                            openGame=False
                            curTeam2=tn
                            Games.append([[curTeam1,curTeam2],[]])
                    elif i==1 or i==2:
                        if not openSet:
                            openSet=True
                            score1=tn
                            if len(line.split(start, 1)[0])<len(line.split(start, 1)[1]):#because of weird formatting
                                pos=0
                            else:
                                pos=1
                        elif openSet:
                            openSet=False
                            if pos==0:
                                Games[-1][1].append([int(score1),int(tn)])
                            else:
                                Games[-1][1].append([int(tn),int(score1)])
    return Games

def names(Games):
    Teams=[]
    for i in Games:
        for t in i[0]:
            if not t in Teams:
                Teams.append(t)
    return Teams